# Workflow explanation — expected contract, not execution evidence

Manual Trigger starts an explicit local run. Synthetic enquiry produces course-owned fixture items. Classify with configured model sends their text as untrusted data to the configured chat endpoint. Validate model result parses an exact three-field object and validates route, FAQ ID and confidence. Allowlisted FAQ lookup reads only the embedded course FAQ; it never dispatches a model-named arbitrary tool. Answerable? routes validated answer candidates to Draft answer; every other valid route goes to Human review draft. Neither output node sends messages.

The expected enquiry-001 branch uses faq-course-access. The refund and instruction-injection fixtures should be held for a person. Those are expectations, not fabricated observations: fill the lab record from actual execution. Any malformed result stops at validation rather than producing a misleading answer. Confidence below 0.8 is routed for review. A missing credential or endpoint/model variable causes a failed request, with no downstream delivery.

No persistent agent memory or MCP connection is used. n8n run history records execution; it is not proof of grounded answers unless the exact node outputs are inspected.
