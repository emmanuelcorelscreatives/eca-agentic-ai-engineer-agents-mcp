# Microsoft agent ecosystem boundaries

AutoGen AgentChat 0.7.5 uses AssistantAgent plus a separate model client; the
application saves/loads agent state explicitly. It is not the older 0.2 API.
Semantic Kernel is a separate SDK for integrating models, plugins and agent
orchestration. No Semantic Kernel implementation is supplied by this stage;
its comparison is conceptual and must not be presented as an executed adapter.
Microsoft Agent Framework has its own Agent, provider clients, sessions,
workflow and middleware abstractions. The genuine Agent constructor is in
s23_framework_agents.py; application routing/approval/checkpoints in
s23_workflow.py are ordinary Python boundaries rather than an SDK workflow.

Migration: instructions map to instructions/system_message; tools need their
actual registration schemas; model-client ownership and close differ; persisted
AutoGen state is not valid Agent Framework session state. Recreate and verify
sessions against the target framework instead of relabelling serialized data.
SDK-native workflow/middleware/approval and Agent Framework persistence must
still be implemented and run before those lessons can be captured as complete.

Official sources:
- https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/index.html
- https://learn.microsoft.com/en-us/agent-framework/
- https://learn.microsoft.com/en-us/semantic-kernel/overview/
