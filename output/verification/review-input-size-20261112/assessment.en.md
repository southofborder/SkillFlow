# Generic source-review input-size acceptance

The current implementation `b3eba2da9823ac8a38620d7a5a728d7b8c66b4f3a5fe14fd7980997923330387` passed 511 scoped tests with 0 skips and zero failures in one final integrated execution. This is not a whole-repository test execution. Earlier focused receipts remain preserved and are not added as duplicate passes.

Only review_display.py, source_review.py and runner.py differ from the accepted baseline production inventory. The reusable shared-v2 default retains all source and contracts and selects packed delivery only when its JSON plus explanation is shorter. Seven normal requests, two workers, Task v5 isolation and existing budgets remain unchanged.

The immutable failed-request reproducer measures 1,079,505 -> 903,775 characters, saving 175,730, with 144,801 below the unchanged 1,048,576 cap. All 16 source files, 344 obligations and 1,195 scopes survive exact serialized roundtrip, and all tracked historical artifacts retain their hashes. No model calls, Skill execution, historical analysis or replay occurred in this offline work.

Coverage includes arbitrary names and counts, nonrepeating inputs, distinct near-duplicates, literal marker collisions, complete and partial materials, original repair coordinates, mandatory contract coverage, exact transport boundaries and zero-start rejection, injected seven-call/two-worker execution, repair/re-review and zero-call replay. Independent review found no blocking issue.

Irreducibly over-limit material still fails explicitly without truncation. Lossless reconstruction does not establish model comprehension. The one newly authorized GA4 will be separate online evidence.

See offline-acceptance.json, tests-final-integrated.xml/.log, integrated-delivery-measurement.json, review-notes.en.md, size-audit/assessment.en.md and docs/doe/review-input-size.md/.zh.md.
