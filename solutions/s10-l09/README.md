# s10-l09 reference: retain history and recover only the known failed step

RecoveryJournal binds the exact old attempt SHA, input SHA, positively retained failure
SHA, distinct reviewer/executor and new attempt identity. It moves the complete old
attempt into same-journal attempt_history and runs only that exact step again. Completed
siblings are reused. Three total attempts is the bound; stale permits, changed input,
UNKNOWN/IN_FLIGHT or any unknown historical attempt are refused.

A known malformed output retains raw_result; a known HTTP response retains actual code
and body. Hidden SDK output without recoverable positive response evidence remains
unknown. No fixture test is a real provider observation. Central QA executes the new
regressions and retains actual results before teaching their success.
