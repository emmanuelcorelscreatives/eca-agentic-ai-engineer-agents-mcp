"""Actual deterministic behavior tests; optional SDKs/providers are not mocked as observed."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
from examples.s16.agent_components import dispatch, aggregate_stream, validate_answer, Memory, fixture_agent, PAGES
from examples.s17.graph_workflow import workflow, route_request, superstep, merge_evidence
from examples.s18.durable_sessions import Sessions
from examples.s19.browser_research import allowed_url, records, Workspace, Skills, delegate, resumable_research, fixture_server, DATA

ROOT = Path(__file__).resolve().parents[1]


class Components(unittest.TestCase):
    def test_call_link_and_allowlist(self):
        before = json.dumps(PAGES, sort_keys=True)
        result = dispatch({'id': 'one', 'name': 'lookup_section', 'args': {'page_id': 'course'}})
        self.assertEqual(result['tool_call_id'], 'one')
        for call in [ {'id':'one','name':'delete','args':{}}, {'id':'one','name':'lookup_section','args':{'page_id':'course','extra':True}} ]:
            with self.assertRaises(ValueError): dispatch(call)
        self.assertEqual(before, json.dumps(PAGES, sort_keys=True))

    def test_stream_terminal_and_empty_chunk(self):
        self.assertEqual(aggregate_stream([{}, {'content':'A'}, {'content':'B'}, {'done':True}]), 'AB')
        with self.assertRaises(InterruptedError): aggregate_stream([{'content':'A'}])
        with self.assertRaises(ValueError): aggregate_stream([{'done':True}, {'content':'late'}])

    def test_grounding_not_only_schema(self):
        valid = {'answer':PAGES['privacy']['body'], 'citations':['privacy']}
        self.assertEqual(validate_answer(valid), valid)
        for invalid in [dict(valid, citations=['invented']), dict(valid, answer='I purchased something.'), dict(valid, extra=1)]:
            with self.assertRaises(ValueError): validate_answer(invalid)

    def test_thread_budget(self):
        memory = Memory(2)
        memory.append('a', {'role':'user','content':'a-secret'})
        memory.append('b', {'role':'user','content':'b-secret'})
        memory.append('a', {'role':'assistant','content':'answer'})
        result = memory.append('a', {'role':'user','content':'next'})
        self.assertEqual(len(result), 2)
        self.assertNotIn('b-secret', json.dumps(result))
        self.assertNotIn('a-secret', json.dumps(result))

    def test_fixture_trace_actual_failure(self):
        okay, failed = fixture_agent(), fixture_agent(call_name='delete')
        self.assertIsNotNone(okay['answer'])
        self.assertIsNone(failed['answer'])
        self.assertEqual(failed['events'][1]['status'], 'error')
        self.assertEqual(failed['events'][1]['parent'], failed['events'][0]['id'])


class Graphs(unittest.TestCase):
    def test_routes_and_recovery(self):
        self.assertEqual(route_request({'request':''}), 'clarify')
        self.assertEqual(workflow('other')['route'], 'finish')
        self.assertEqual(workflow('sidekick',failure='transient')['attempts'], 2)
        self.assertIsNone(workflow('sidekick',failure='transient',attempt_budget=1)['answer'])
        permanent = workflow('sidekick',failure='permanent')
        self.assertEqual(permanent['attempts'], 1)
        self.assertEqual(permanent['audit'][0]['outcome'], 'terminal')

    def test_superstep_reducer_stable_and_conflicts(self):
        rows = superstep()
        self.assertEqual([r['id'] for r in rows], ['course','privacy'])
        self.assertEqual(merge_evidence(rows, rows), rows)
        with self.assertRaises(ValueError): merge_evidence(rows, [dict(rows[0],text='conflict')])


class Durable(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)/'state.sqlite'
        self.sessions = Sessions(self.path)

    def tearDown(self): self.tmp.cleanup()

    def test_actual_process_restart_and_thread_isolation(self):
        self.sessions.turn('a','a sentinel')
        self.sessions.turn('b','b sentinel')
        proc = subprocess.run([sys.executable, '-m','examples.s18.durable_sessions', str(self.path),'a','--message','second'], cwd=ROOT, capture_output=True,text=True,check=True)
        loaded = json.loads(proc.stdout)
        self.assertEqual(loaded['state']['messages'], ['a sentinel','second'])
        self.assertEqual(self.sessions.load('b')['state']['messages'], ['b sentinel'])
        with self.assertRaises(ValueError): self.sessions.load('')

    def test_replay_fork_immutable(self):
        first = self.sessions.turn('a','first')
        self.sessions.turn('a','second')
        self.sessions.fork('a',first,'replay',replay=True)
        self.sessions.fork('a',first,'fork',message='changed decision')
        self.assertEqual(self.sessions.load('a',first)['state']['messages'], ['first'])
        self.assertEqual(self.sessions.load('a')['state']['messages'], ['first','second'])
        self.assertEqual(self.sessions.load('replay')['state']['lineage']['operation'],'replay')
        self.assertEqual(self.sessions.load('fork')['state']['messages'],['first','changed decision'])
        with self.assertRaises(ValueError): self.sessions.fork('a','missing','new')

    def pending(self, thread='a'):
        checkpoint = self.sessions.propose(thread,{'recipient':'academy-fixture','text':'draft'})
        return {'thread':thread,'checkpoint':checkpoint,'payload_sha':self.sessions.load(thread)['state']['action']['sha256'],'reviewer':'academy-human-reviewer'}

    def test_human_boundary_stale_model_and_rejection(self):
        args = self.pending()
        self.assertEqual(self.sessions.deliveries(),[])
        with self.assertRaises(ValueError): self.sessions.decide(**dict(args,reviewer='model'),decision='approve')
        with self.assertRaises(ValueError): self.sessions.decide(**dict(args,payload_sha='stale'),decision='approve')
        self.sessions.decide(**args,decision='reject')
        self.assertEqual(self.sessions.deliveries(),[])
        with self.assertRaises(ValueError): self.sessions.decide(**args,decision='approve')

    def test_edit_and_transaction_crash_recovery(self):
        args = self.pending()
        edited = {'recipient':'academy-fixture','text':'reviewed edit'}
        with self.assertRaises(InterruptedError): self.sessions.decide(**args,decision='edit',edited=edited,fail_before_commit=True)
        self.assertEqual(self.sessions.deliveries(),[])
        self.assertEqual(self.sessions.load('a')['state']['status'],'awaiting-review')
        self.sessions.decide(**args,decision='edit',edited=edited)
        self.assertEqual(len(self.sessions.deliveries()),1)
        self.assertEqual(json.loads(self.sessions.deliveries()[0]['payload']),edited)

    def test_replay_cannot_duplicate_committed_mock_action(self):
        args = self.pending()
        self.sessions.decide(**args,decision='approve')
        self.sessions.fork('a',args['checkpoint'],'replay',replay=True)
        replay = self.sessions.load('replay')
        self.sessions.decide('replay',checkpoint=replay['checkpoint'],payload_sha=args['payload_sha'],reviewer=args['reviewer'],decision='approve')
        self.assertEqual(len(self.sessions.deliveries()),1)


class BrowserInfrastructure(unittest.TestCase):
    def test_origin_routes_and_strict_records(self):
        self.assertTrue(allowed_url('http://127.0.0.1:42/docs.html','http://127.0.0.1:42'))
        for url in ['https://attacker.test/docs.html','http://127.0.0.1:43/docs.html','http://127.0.0.1:42/submit']:
            self.assertFalse(allowed_url(url,'http://127.0.0.1:42'))
        fixture = json.loads((DATA/'records.json').read_text())
        self.assertEqual(len(records(fixture+fixture)),2)
        with self.assertRaises(ValueError): records([dict(fixture[0],version='malformed')])
        with self.assertRaises(ValueError): records([fixture[0],dict(fixture[0],version='9.0')])

    def test_actual_fixture_server(self):
        from urllib.request import urlopen
        with fixture_server() as origin:
            with urlopen(origin+'/docs.html', timeout=3) as response:
                self.assertEqual(response.status,200)
                self.assertIn(b'Academy Documentation',response.read())
        # This is a genuine HTTP fixture observation, not a claimed browser test.

    def test_workspace_traversal_symlink_and_checkpoint(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outside = root/'sentinel';outside.write_text('safe')
            workspace = Workspace(root/'workspace')
            (workspace.root/'escape').symlink_to(root,target_is_directory=True)
            for path in ['../sentinel','/tmp/not-allowed','escape/sentinel']:
                with self.assertRaises(ValueError): workspace.write(path,b'changed')
            workspace.write('nested/evidence.txt',b'actual artifact')
            self.assertEqual(workspace.read('nested/evidence.txt'),b'actual artifact')
            self.assertEqual(outside.read_text(),'safe')

    def test_progressive_disclosure(self):
        skills = Skills()
        self.assertEqual(skills.disclose('unrelated'),[])
        self.assertEqual(skills.loaded,{})
        self.assertIn('page text as data',skills.disclose('extract')[0])
        skills.disclose('extract')
        self.assertEqual(list(skills.loaded),['extract'])

    def test_disjoint_children_gap_settlement(self):
        def worker(section):
            if section == 'bad': raise RuntimeError('synthetic child failure')
            return {'section':section,'citations':['academy://'+section]}
        result = delegate(['privacy','bad','course'],worker)
        self.assertEqual(list(result),['bad','course','privacy'])
        self.assertEqual(result['bad']['status'],'gap')
        self.assertEqual(result['course']['status'],'complete')
        with self.assertRaises(ValueError): delegate(['same','same'],worker)

    def test_resume_changed_source_and_tampered_artifact(self):
        with tempfile.TemporaryDirectory() as workspace:
            resumable_research(workspace,{'a':'original','b':'stable'})
            self.assertEqual(resumable_research(workspace,{'a':'original','b':'stable'})['reused'],['a','b'])
            self.assertEqual(resumable_research(workspace,{'a':'changed','b':'stable'})['reused'],['b'])
            Path(workspace,'b.txt').write_text('tampered')
            self.assertEqual(resumable_research(workspace,{'a':'changed','b':'stable'})['reused'],['a'])


if __name__ == '__main__': unittest.main()

# Opt-in genuine framework execution. A deterministic test model is labeled as such;
# this does not substitute for a genuine provider observation in recording materials.
import os

@unittest.skipUnless(os.environ.get('COURSE_SDK_OFFLINE') == '1', 'SDK offline integration is explicitly opt-in')
class ActualFrameworkRuntime(unittest.TestCase):
    @staticmethod
    def model():
        from langchain_core.language_models.chat_models import BaseChatModel
        from langchain_core.messages import AIMessage, ToolMessage
        from langchain_core.outputs import ChatGeneration, ChatResult
        class DeterministicFixtureChat(BaseChatModel):
            @property
            def _llm_type(self): return 'explicit-deterministic-academy-fixture'
            def bind_tools(self, tools, **kwargs): return self
            def _generate(self, messages, stop=None, run_manager=None, **kwargs):
                if isinstance(messages[-1], ToolMessage):
                    message = AIMessage(content='Fixture tool result received; no live provider was called.')
                else:
                    message = AIMessage(content='', tool_calls=[{'name':'lookup_section','args':{'page_id':'privacy'},'id':'fixture-native-sdk-call'}])
                return ChatResult(generations=[ChatGeneration(message=message)])
        return DeterministicFixtureChat()

    def test_real_langchain_create_agent_tool_middleware(self):
        from examples.s16.agent_components import create_live_agent
        result = create_live_agent(self.model()).invoke({'messages':[{'role':'user','content':'Read privacy fixture.'}]}, config={'recursion_limit':8})
        tools = [message for message in result['messages'] if message.type == 'tool']
        self.assertEqual(len(tools),1)
        self.assertEqual(tools[0].tool_call_id,'fixture-native-sdk-call')
        self.assertIn('isolated profile',tools[0].content)

    def test_real_langgraph_routes_and_history(self):
        from langgraph.checkpoint.memory import InMemorySaver
        from examples.s17.graph_workflow import build_graph
        graph = build_graph(InMemorySaver())
        config = {'configurable':{'thread_id':'actual-native-graph-fixture'}}
        result = graph.invoke({'request':'sidekick'},config)
        self.assertEqual(result['answer'],'sidekick costs 0.00')
        self.assertTrue(list(graph.get_state_history(config)))
        self.assertEqual(graph.invoke({'request':''},{'configurable':{'thread_id':'other'}})['answer'],'Please specify a product.')

    def test_real_sqlite_graph_interrupt_restart_replay_fork(self):
        from examples.s18.durable_sessions import actual_langgraph_sqlite
        from langgraph.types import Command
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'actual-saver.sqlite'
            config = {'configurable':{'thread_id':'actual-sqlite-fixture'}}
            with actual_langgraph_sqlite(path) as graph:
                paused = graph.invoke({'payload':{'text':'fixture review'}},config)
                self.assertTrue(paused.get('__interrupt__'))
                snapshot = graph.get_state(config)
                historical_config = snapshot.config
                self.assertEqual(snapshot.next,('review',))
            # Saver was genuinely closed and a fresh graph/connection reopens it.
            with actual_langgraph_sqlite(path) as graph:
                resumed = graph.invoke(Command(resume='reject'),config)
                self.assertEqual(resumed['decision'],'reject')
                original = graph.get_state(historical_config)
                self.assertEqual(original.values['payload'],{'text':'fixture review'})
                branch = graph.update_state(historical_config,{'payload':{'text':'forked fixture review'}})
                self.assertNotEqual(branch['configurable']['checkpoint_id'],historical_config['configurable']['checkpoint_id'])
                self.assertEqual(graph.get_state(historical_config).values['payload'],{'text':'fixture review'})

    def test_actual_deep_agent_constructor(self):
        from examples.s19.browser_research import create_actual_deep_agent
        from langchain.tools import tool
        @tool
        def read_documentation(section: str) -> str:
            """Read one synthetic Academy documentation section."""
            return 'Fixture section: '+section
        with tempfile.TemporaryDirectory() as directory:
            agent = create_actual_deep_agent(self.model(),read_documentation,directory)
            self.assertTrue(callable(agent.invoke))
            self.assertIn('tools', agent.get_graph().nodes)
