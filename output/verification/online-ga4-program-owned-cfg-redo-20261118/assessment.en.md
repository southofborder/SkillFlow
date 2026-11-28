# GA4 replacement 162541

The replacement started at 16:25 China time on November 18, 2026. Both processing requests returned complete answers. The finite correction left 481 structurally valid modeled IR records. The sensitivity submission was rejected locally at 1,107,518 characters, 58,942 over the 1,048,576-character cap. Analysis ended after 2,252.375 seconds. Its one offline replay matched in 47.509 seconds with zero new native starts. [Backend audit](final-backend-audit.json) · [Integrity check](final-integrity.json)

The run used the offline accepted implementation `d440dd8ce37b259da8ae6b36a1dde10ae876286bc187c22501156a4f53995523`, the accepted Task and flow, the original 215-block, 489-IR, 192-edge CFG, and all 16 source files from closed run 205158. The experiment retained original producer provenance, seven normal semantic stages including three inherited stages, and two workers. Terminal checks verified 221 runtime pins, all three executables, 83 inherited originals, 103 inherited copies, and exit of all four recorded PIDs. [Integrity check](final-integrity.json)

| Delivery | Characters | Native elapsed | Public input tokens | Public output tokens |
| --- | ---: | ---: | ---: | ---: |
| Initial processing | 431,150 | 1,518.733 seconds | 142,507 | 45,000 |
| Finite processing correction | 457,036 | 688.824 seconds | 151,768 | 10,653 |
| Sensitivity | 1,107,518 | Rejected before start | N/A | N/A |

All three deliveries contained the complete 16-file source. The two native starts produced 349,928 public tokens, including 290,816 cached input and 7,961 reasoning output tokens as subsets. The logs show four internal sampling retries, one overlapping WebSocket connection failure, and zero outer retries. Failed internal usage, actual charges, and pure generation time are unknown. The third new logical request was the local sensitivity rejection. Task correspondence was interrupted before its first logical call. The three inherited logical requests are accounted for separately. [Request audit](final-request-audit.json)

Processing validation found 19 issues across 12 IR in the first answer. The correction offered six whole-record slots and six output-binding fields. The returned six record replacements resolved 13 issues and introduced zero new structural diagnostics. The six missing field updates remained invalid and were isolated. The final partial fragment contains 481 modeled IR and eight unmodeled IR, including two source-backed gaps. The finite correction delivery was 143,031 characters smaller than the full candidate correction in 205158, a 23.84% descriptive reduction across different model answers and diagnostics. [Processing audit](processing-scope-audit.json)

The expanded processing JSON accounted for 702,536 characters, the CFG for 214,251, and the full numbered source for 180,825. Expanded processing contributed the entire 230,640-character increase over sensitivity in 205158. Task correspondence was interrupted before launch, with a saved 1,164,111-character prompt body using the same expanded rendering path. Offline prototypes with the existing lossless encoding and decoder guidance rendered sensitivity at 494,748 characters and task correspondence at 540,464 characters. The structured inputs round-tripped exactly, and the source and output instructions matched. [Size audit](sensitivity-size-audit.json)

The run ended before source review, a selected annotation, CFG revision, propagation, input necessity, and DOE. The measured finite processing correction exercised scoped delivery and merge, with remaining unresolved fields. The original 153823 attempt ended at the 2,700.073-second processing process deadline without public usage. [Original attempt](../online-ga4-program-owned-cfg-20261118/assessment.en.md)
