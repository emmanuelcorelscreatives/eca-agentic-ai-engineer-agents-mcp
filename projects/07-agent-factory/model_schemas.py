"""Typed handoffs for the model-driven Stage 25 factory.

Validation is engineering evidence, not proof that generated code is safe.
"""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class Closed(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)

class Requirement(Closed):
    id:str=Field(pattern=r'^REQ-[A-Z0-9-]+$')
    source:str
    criterion:str=Field(min_length=1,max_length=4000)
    acceptance_test:str=Field(pattern=r'^test_[a-z0-9_]+$')

class RequirementsProposal(Closed):
    spec_sha256:str=Field(pattern=r'^[a-f0-9]{64}$')
    requirements:list[Requirement]=Field(min_length=1,max_length=100)
    unresolved:list[str]=Field(max_length=30)

class Component(Closed):
    path:str
    requirement_ids:list[str]=Field(min_length=1,max_length=100)
    purpose:str=Field(min_length=1,max_length=2000)

class ArchitectureProposal(Closed):
    requirements_sha256:str=Field(pattern=r'^[a-f0-9]{64}$')
    framework:Literal['stdlib','agno','mastra']
    entry_point:str
    components:list[Component]=Field(min_length=1,max_length=60)
    unresolved:list[str]=Field(max_length=30)

class Artifact(Closed):
    path:str
    content:str=Field(max_length=100000)
    requirement_ids:list[str]=Field(min_length=1,max_length=100)

class ArtifactProposal(Closed):
    architecture_sha256:str=Field(pattern=r'^[a-f0-9]{64}$')
    artifacts:list[Artifact]=Field(min_length=1,max_length=40)
    unresolved:list[str]=Field(max_length=30)

class InstructionProposal(Closed):
    architecture_sha256:str=Field(pattern=r'^[a-f0-9]{64}$')
    role:str=Field(min_length=1,max_length=2000)
    goals:list[str]=Field(min_length=1,max_length=30)
    allowed_tools:list[str]=Field(min_length=1,max_length=20)
    policies:list[str]=Field(min_length=1,max_length=30)
    refusal:str=Field(min_length=1,max_length=2000)
    escalation:str=Field(min_length=1,max_length=2000)
    untrusted_data:str=Field(min_length=1,max_length=2000)

class ReviewFinding(Closed):
    path:str
    line:int=Field(ge=1)
    severity:Literal['blocking','warning','note']
    requirement_id:str
    evidence:str=Field(min_length=1,max_length=4000)
    proposed_correction:str=Field(min_length=1,max_length=4000)

class ReviewProposal(Closed):
    artifact_sha256:str=Field(pattern=r'^[a-f0-9]{64}$')
    findings:list[ReviewFinding]=Field(max_length=100)
    covered_requirement_ids:list[str]=Field(min_length=1,max_length=100)
    limitations:list[str]=Field(min_length=1,max_length=30)

class RepairProposal(Closed):
    failed_artifact_sha256:str=Field(pattern=r'^[a-f0-9]{64}$')
    replacements:list[Artifact]=Field(min_length=1,max_length=10)
    diagnostic_explanation:str=Field(min_length=1,max_length=4000)
