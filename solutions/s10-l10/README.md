# s10-l10 reference: own-session export and deployment

`interface_v3` mounts the export control and file output. `RunExports` binds server session, opaque run token, exact completed checkpoint and report SHA; it invokes `exports_v2.export`. Download preparation rechecks session, fixed paths, unchanged state and file hashes. Foreign, incomplete, tampered and symlinked exports must fail.

The v3 Dockerfile starts `deploy_v3` and installs the supplied transitive hash lock. Follow the [v3 deployment guide](../../projects/03-deep-research/deployment/research-v3/README.md); do not confuse this checked-in lock with the older v2 deployment's separate requirements. Check actual build, health, private-state persistence and a fresh-session report/download. A declared Dockerfile, locked dependency file, UI constructor or offline callback test does not establish successful live model/search/browser/deployment behavior.
