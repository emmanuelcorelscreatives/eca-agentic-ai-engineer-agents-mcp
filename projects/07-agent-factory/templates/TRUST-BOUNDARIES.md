# Factory trust boundaries

Approved typed spec → SHA-bound requirements → approved architecture → fresh scaffold → tools/instructions/tests → static diagnostics → explicit Docker execution → bounded repair → release decision.

Every file is content hashed with the spec and approval inputs. Model output is untrusted data. A human-approved spec does not approve generated code. Static diagnostics do not prove security. Fixed maintained templates can be exercised on the host only after exact complete-file equality; arbitrary generated or repaired code must use the bounded Docker validator. Docker runs need a separately approved digest-pinned image and explicit authorization; no implicit image download, dependency installation, build or network access occurs.

The deterministic research/support fixtures demonstrate engineering contracts, never model reasoning or quality. Agno and Mastra are supported specification selections but require independently verified adapter implementations and locked dependency smoke runs before release. Unknown capability requests fail closed.
