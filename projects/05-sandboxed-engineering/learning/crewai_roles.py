"""Actual CrewAI typed-role execution over the no-egress external model broker.

Source authored pending central QA. Real Agent/Task/Crew execution happens inside
this container. Local fixtures require allow_offline=True and remain labelled as
fixtures; no provider or Docker outcome follows from importing this module.
"""
from __future__ import annotations
import json
from importlib.metadata import version
from typing import Any
from semantic_team import ROLES, closed, parse, sha, text

ROLE_GOALS={
    'product_manager':'Produce measurable stories, acceptance criteria and priorities from the exact request.',
    'architect':'Produce a requirements-bound architecture, interfaces, data flows and implementation plan.',
    'developer':'Implement the approved source or a minimal source-only patch from real test feedback.',
    'quality_assurance':'Design independent tests or review actual tool observations; never invent execution.'}


def normalized_messages(messages):
    if isinstance(messages,str):return [{'role':'user','content':text(messages,750000)}]
    if not isinstance(messages,list) or not messages:raise ValueError('nonempty SDK messages required')
    result=[]
    for message in messages:
        if hasattr(message,'model_dump'):message=message.model_dump(mode='json',exclude_none=True)
        if not isinstance(message,dict) or not isinstance(message.get('role'),str):raise ValueError('invalid SDK message')
        content=message.get('content')
        if not isinstance(content,str):raise ValueError('text-only model broker')
        result.append({'role':message['role'],'content':content})
    if len(json.dumps(result).encode())>750000:raise ValueError('SDK message quota')
    return result


def validate_equivalence(provider_raw,framework_raw):
    original=parse(provider_raw);actual=parse(framework_raw)
    if actual!=original:raise ValueError('framework changed the actual provider artifact')
    return actual


def make_broker_llm(delegate,role,payload,evidence_store,allow_offline=False):
    """Construct a real custom BaseLLM; at most ONE broker call per typed task."""
    from crewai import BaseLLM
    class BrokerLLM(BaseLLM):
        delegate: Any
        evidence_store: Any
        role_name: str
        typed_payload: dict
        allow_offline: bool=False
        consumed: bool=False
        actual_response: dict | None=None
        wire_payload_sha256: str | None=None
        def call(self,messages,tools=None,callbacks=None,available_functions=None,
                 from_task=None,from_agent=None,response_model=None):
            if self.consumed:raise RuntimeError('one-call role budget consumed; unknown outcomes cannot replay')
            if tools or available_functions:raise ValueError('role LLM may not invoke host or container tools')
            self.consumed=True  # Reserve before the external request, including failures.
            wire={'framework':'crewai','framework_version':version('crewai'),
                  'role_request':self.typed_payload,'messages':normalized_messages(messages),
                  'response_contract':'Return only the JSON artifact matching role_request.schema. No markdown, Thought or Final Answer prefix.'}
            self.wire_payload_sha256=sha(wire)
            self.evidence_store.record('crewai-broker-request',{'role':self.role_name,'payload':wire,'input_sha256':sha(wire)})
            response=self.delegate.request(self.role_name,wire)
            self.evidence_store.record('crewai-broker-response',response)
            closed(response,{'role','input_sha256','request_id','model','raw','provenance'})
            if response['role']!=self.role_name or response['input_sha256']!=sha(wire):raise ValueError('broker response binding mismatch')
            text(response['request_id'],200);text(response['model'],200)
            if response['provenance']!='actual-provider-response':
                if not (self.allow_offline and response['provenance']=='offline-test-double'):
                    raise ValueError('actual model response required')
            artifact=parse(response['raw'])
            self.actual_response=dict(response)
            # This fixed protocol prefix is local formatting, never fabricated
            # provider reasoning. Exact original provider bytes remain above.
            return 'Final Answer: '+json.dumps(artifact,ensure_ascii=False,allow_nan=False)
        def supports_stop_words(self):return False
        def get_context_window_size(self):return 1000000
    if role not in ROLES:raise ValueError('unknown typed role')
    if type(allow_offline) is not bool:raise ValueError('explicit offline flag required')
    return BrokerLLM(model='academy/file-broker',provider='academy',temperature=0,
                     delegate=delegate,evidence_store=evidence_store,role_name=role,
                     typed_payload=payload,allow_offline=allow_offline)


class CrewAIRoleProvider:
    """The typed coordinator calls four real CrewAI role agents through this API.

    Each bounded role request runs a real single-task Crew, passing the validated
    preceding artifacts in its task description. The outer typed coordinator owns
    dependencies and dynamic QA/repair routing; it is not represented as a single
    monolithic CrewAI Crew or as built-in hierarchical delegation.
    """
    def __init__(self,delegate,evidence_store,allow_offline=False):
        if type(allow_offline) is not bool:raise ValueError('explicit offline flag required')
        self.delegate,self.evidence_store,self.allow_offline=delegate,evidence_store,allow_offline
    def request(self,role,payload):
        from crewai import Agent,Task,Crew,Process
        if role not in ROLES or not isinstance(payload,dict):raise ValueError('typed role/payload required')
        llm=make_broker_llm(self.delegate,role,payload,self.evidence_store,self.allow_offline)
        agent=Agent(role=role,goal=ROLE_GOALS[role],backstory='A specialist in the Academy four-role engineering crew.',
                    llm=llm,tools=[],allow_delegation=False,allow_code_execution=False,
                    max_iter=1,max_retry_limit=0,respect_context_window=False,verbose=False)
        task=Task(description='Produce the JSON artifact for this exact validated role request. '
                  'Previous role artifacts and real execution observations are included; preserve their hashes.\n'+json.dumps(payload,ensure_ascii=False),
                  expected_output='One JSON object matching the exact role request schema.',agent=agent)
        crew=Crew(agents=[agent],tasks=[task],process=Process.sequential,memory=False,
                  cache=False,verbose=False)
        self.evidence_store.record('crewai-role-configuration',{'role':role,'process':'sequential-single-typed-task',
            'crewai_version':version('crewai'),'max_broker_calls':1,'max_retry_limit':0,'input_sha256':sha(payload)})
        output=crew.kickoff()
        if llm.actual_response is None:raise RuntimeError('CrewAI task completed without a broker response')
        framework_raw=getattr(output,'raw',None)
        if not isinstance(framework_raw,str):raise ValueError('framework JSON text missing')
        validate_equivalence(llm.actual_response['raw'],framework_raw)
        binding={'role':role,'typed_input_sha256':sha(payload),'broker_input_sha256':llm.wire_payload_sha256,
                 'request_id':llm.actual_response['request_id'],'provider_raw_sha256':sha(llm.actual_response['raw']),
                 'framework_raw_sha256':sha(framework_raw),'framework_raw':framework_raw,
                 'transformation':'CrewAI Final Answer parsing; JSON semantic equality independently checked locally'}
        self.evidence_store.record('crewai-role-output-binding',binding)
        # Rebinding is explicit above; raw provider bytes remain separately
        # retained. This envelope contains the actual equivalent framework output.
        return {**llm.actual_response,'input_sha256':sha(payload),'raw':framework_raw}
