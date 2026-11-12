"""Stage 23 native Microsoft Agent Framework 1.16.1 components.

Inject an SDK client; importing this module never creates credentials or calls a
provider. Scripted clients in tests exercise the real SDK, not model reasoning.
AutoGen save_state/load_state remains a separate format in s23_framework_agents.
"""
import hashlib
import json
import os
import re
import tempfile
import time
from pathlib import Path
from typing import Literal, Never
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field
from agent_framework import (
    Agent, AgentSession, AgentMiddleware, ChatMiddleware, FunctionMiddleware,
    Executor, WorkflowBuilder, WorkflowContext, handler, tool,
)
from agent_framework import MiddlewareFailure


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Ticket(StrictModel):
    ticket_id: str = Field(min_length=1)
    category: Literal["damaged", "delivery", "unknown"]
    product_id: str = Field(min_length=1)
    message: str = Field(min_length=1)


class Decision(StrictModel):
    ticket_id: str = Field(min_length=1)
    category: Literal["damaged", "delivery", "unknown"]
    recommendation: str = Field(min_length=1)
    held: bool


class Handoff(StrictModel):
    request: Ticket
    research: Decision


class Escalation(StrictModel):
    ticket_id: str = Field(min_length=1)
    draft: str = Field(min_length=1)


def payload_key(payload: Escalation) -> str:
    return hashlib.sha256(payload.model_dump_json().encode()).hexdigest()


class ApprovalLedger:
    """Trusted UI/controller supplies grant; model arguments cannot grant it.

    Exactly one local outbox append is permitted per approved immutable payload.
    The outbox is a synthetic local effect, never an email/network send.
    """
    def __init__(self):
        self.grants = {}
        self.effects = []

    def approve(self, payload: Escalation, reviewer: str):
        if not reviewer.strip():
            raise ValueError("A named reviewer is required")
        self.grants[payload_key(payload)] = reviewer

    def apply(self, payload: Escalation):
        reviewer = self.grants.pop(payload_key(payload), None)
        if reviewer is None:
            raise MiddlewareFailure("Exact payload approval absent or already consumed")
        self.effects.append({**payload.model_dump(), "reviewer": reviewer})
        return {"recorded_locally": True, "sent": False}


class ApprovalBoundary(FunctionMiddleware):
    def __init__(self, ledger):
        self.ledger = ledger

    async def process(self, context, call_next):
        if context.function.name == "record_escalation":
            payload = Escalation.model_validate(dict(context.arguments))
            if payload_key(payload) not in self.ledger.grants:
                raise MiddlewareFailure("Human confirmation required for this exact payload")
        await call_next()


def tools_for(ledger):
    @tool
    def policy_lookup(product_id: str) -> dict:
        """Read the Academy's synthetic retail policy for a known product."""
        from examples.s22_policy import PolicyService
        return PolicyService().lookup(product_id)

    @tool
    def record_escalation(ticket_id: str, draft: str) -> dict:
        """Record an exact human-approved draft in the local practice outbox."""
        return ledger.apply(Escalation(ticket_id=ticket_id, draft=draft))

    return [policy_lookup, record_escalation]


class Telemetry:
    """Allowlist telemetry: never stringify messages, arguments or exceptions.

    Explicit canary secrets are redacted even from correlation identifiers.
    Only duration, phase, correlation and success/failure class are retained.
    """
    def __init__(self, correlation=None, secrets=()):
        self.secrets = tuple(secrets)
        self.correlation = self.clean(correlation or str(uuid4()))
        self.events = []

    def clean(self, value):
        for secret in self.secrets:
            if secret:
                value = value.replace(secret, "[REDACTED]")
        return re.sub(r"(?i)(bearer\s+)[^\s]+", r"\1[REDACTED]", value)

    async def observe(self, phase, call_next):
        start = time.perf_counter_ns()
        outcome = "ok"
        try:
            await call_next()
        except BaseException:
            outcome = "error"
            raise
        finally:
            self.events.append({"phase": phase, "correlation": self.correlation,
                                "duration_ns": time.perf_counter_ns() - start,
                                "outcome": outcome})


class AgentTiming(AgentMiddleware):
    def __init__(self, telemetry):
        self.telemetry = telemetry

    async def process(self, context, call_next):
        await self.telemetry.observe("agent", call_next)


class ChatTiming(ChatMiddleware):
    def __init__(self, telemetry):
        self.telemetry = telemetry

    async def process(self, context, call_next):
        await self.telemetry.observe("model", call_next)


class ToolTiming(FunctionMiddleware):
    def __init__(self, telemetry):
        self.telemetry = telemetry

    async def process(self, context, call_next):
        await self.telemetry.observe("tool", call_next)


def build_specialist(client, name, telemetry, ledger):
    return Agent(client=client, name=name,
                 instructions=(f"You are the Academy {name} specialist. Use policy_lookup. "
                               "Return Decision JSON for the exact ticket/category. "
                               "Never invent delivery observations; hold unknowns. "
                               "record_escalation requires separate human approval."),
                 tools=tools_for(ledger),
                 middleware=[AgentTiming(telemetry), ChatTiming(telemetry),
                             ToolTiming(telemetry), ApprovalBoundary(ledger)])


async def decide(agent, ticket: Ticket, session=None, research=None):
    # SDK response_format makes the SDK parse/validate its response. Revalidate
    # and bind identity because a valid schema alone cannot prevent ticket drift.
    prompt = ticket.model_dump_json()
    if research is not None:
        prompt += "\nResearch to independently review:\n" + research.model_dump_json()
    response = await agent.run(prompt, session=session, options={"response_format": Decision})
    result = Decision.model_validate_json(response.text)
    if (result.ticket_id, result.category) != (ticket.ticket_id, ticket.category):
        raise ValueError("Response belongs to a different ticket/category")
    if ticket.category == "unknown" and not result.held:
        raise ValueError("Ambiguous ticket must remain held")
    return result


def save_session(path: Path, owner: str, session: AgentSession):
    """SDK serialization plus application ownership; no credentials in envelope."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    envelope = {"framework": "microsoft-agent-framework/1.16.1", "owner": owner,
                "session": session.to_dict()}
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".session-")
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(envelope, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_session(path: Path, owner: str):
    envelope = json.loads(Path(path).read_text())
    if envelope["framework"] != "microsoft-agent-framework/1.16.1" or envelope["owner"] != owner:
        raise ValueError("Wrong framework or session owner")
    return AgentSession.from_dict(envelope["session"])


class Intake(Executor):
    @handler
    async def route(self, ticket: Ticket, ctx: WorkflowContext[Ticket, Decision]):
        if ticket.category == "unknown":
            await ctx.yield_output(Decision(ticket_id=ticket.ticket_id, category="unknown",
                                           recommendation="Request clarification", held=True))
        else:
            await ctx.send_message(ticket)


class Research(Executor):
    def __init__(self, agent, **kwargs):
        super().__init__(**kwargs)
        self.agent = agent

    @handler
    async def process(self, ticket: Ticket, ctx: WorkflowContext[Handoff]):
        result = await decide(self.agent, ticket)
        await ctx.send_message(Handoff(request=ticket, research=result))


class Review(Executor):
    def __init__(self, agent, **kwargs):
        super().__init__(**kwargs)
        self.agent = agent

    @handler
    async def process(self, handoff: Handoff, ctx: WorkflowContext[Never, Decision]):
        await ctx.yield_output(await decide(self.agent, handoff.request, research=handoff.research))


def build_workflow(client_factory, telemetry=None, ledger=None):
    """Native typed graph: route -> category researcher -> shared reviewer.

    Both category branches contain actual SDK agents. Unknowns yield a held
    result without calling any model. Every branch shares contracts and policies.
    """
    telemetry, ledger = telemetry or Telemetry(), ledger or ApprovalLedger()
    intake = Intake(id="intake")
    damage = Research(build_specialist(client_factory("damage"), "damage", telemetry, ledger), id="damage")
    delivery = Research(build_specialist(client_factory("delivery"), "delivery", telemetry, ledger), id="delivery")
    review = Review(build_specialist(client_factory("review"), "review", telemetry, ledger), id="review")
    return (WorkflowBuilder(start_executor=intake)
            .add_edge(intake, damage, condition=lambda ticket: ticket.category == "damaged")
            .add_edge(intake, delivery, condition=lambda ticket: ticket.category == "delivery")
            .add_edge(damage, review).add_edge(delivery, review).build())
