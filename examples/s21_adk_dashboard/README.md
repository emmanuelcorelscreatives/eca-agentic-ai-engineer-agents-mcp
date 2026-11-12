# Actual ADK development app

From repository root, install the pinned Google ADK environment, set GOOGLE_MODEL
and configure its matching provider credentials. Set PYTHONPATH to repository root.
Run `adk web examples/s21_adk_dashboard --host 127.0.0.1 --port 8766`.
The package exports an actual ADK root_agent, sharing the same stock/delivery tools.
Observe and retain a real request event trace and invalid-SKU tool failure before
recording this lesson. Dashboard startup and provider requests remain unverified
until the SDK integration receipt says otherwise. InMemorySessionService in the
CLI example provides process-local state only; do not claim restart persistence.
