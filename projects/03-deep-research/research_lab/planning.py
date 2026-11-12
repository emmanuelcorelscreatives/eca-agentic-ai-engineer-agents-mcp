"""Explicit task contracts, dependency checks and focused queries."""
from dataclasses import dataclass, asdict

ROLES = {"planner": ("question", "plan"), "searcher": ("query", "sources"),
         "analyst": ("evidence", "findings"), "reviewer": ("findings", "quality"),
         "writer": ("quality", "report")}

def make_plan(question):
    if not isinstance(question, str) or not question.strip():
        raise ValueError("a non-empty question is required")
    tasks = [{"id": f"task-{i}", "objective": topic, "dependencies": [],
              "completion": "collect cited evidence or explicitly record a gap"}
             for i, topic in enumerate(("accessibility", "cost", "operations"), 1)]
    return {"schema_version": 1, "question": question.strip(), "scope": "community workshop scheduling",
            "acceptance": ["all findings cited", "contradictions retained", "unknowns explicit"],
            "tasks": tasks, "findings": []}

def validate_plan(plan):
    tasks = plan["tasks"]
    ids = [t["id"] for t in tasks]
    if len(set(ids)) != len(ids) or not tasks:
        raise ValueError("unique tasks required")
    edges = {t["id"]: t["dependencies"] for t in tasks}
    seen, visiting = set(), set()
    def visit(key):
        if key not in edges or key in visiting:
            raise ValueError("missing or cyclic dependency")
        if key in seen: return
        visiting.add(key)
        for dependency in edges[key]: visit(dependency)
        visiting.remove(key); seen.add(key)
    for key in ids: visit(key)
    if not plan.get("acceptance") or not plan.get("scope"):
        raise ValueError("scope and acceptance required")
    return plan

def queries_for(plan):
    validate_plan(plan)
    return [{"id": f"q-{i}-{intent}", "task_id": task["id"], "intent": intent,
             "text": f'{plan["question"]} {task["objective"]} {suffix}'}
            for i, task in enumerate(plan["tasks"], 1)
            for intent, suffix in (("support", "evidence"), ("counterevidence", "limitations alternatives"))]
