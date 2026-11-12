# s10-l10 reference: owned-session export and real deployment proof

interface_v3 mounts a real export button and file output. RunExports binds server session,
opaque run token, exact completed checkpoint and report SHA; it invokes exports_v2.export
rather than introducing another renderer. Download preparation rechecks session, fixed
paths, unchanged state and file hashes. Foreign/incomplete/tampered/symlinked exports fail.

The v3 Dockerfile starts deploy_v3. Its exact direct-version requirements input still
needs central actual transitive hash-lock resolution and clean startup/health/persistence
proof. A genuine fresh-session actual report/export remains required; offline constructor
or callback tests alone cannot certify live model/Brave/browser/deployment completion.
