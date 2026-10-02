# 首阶段覆盖矩阵

由 tools/build_catalog.py 从外置事实标注生成。每行对应覆盖目标、样例、事实及其原文证据；不代表语义判定已通过。

| 覆盖目标 | 样例 | 事实 | 原文位置（包内路径，1 起始行号） |
| --- | --- | --- | --- |
| actual_behavior | R01 | [R01-F01](annotations/R01.json) | [SKILL.md:14-20](inputs/upstream/pdf/SKILL.md#L14) |
| actual_behavior | R02 | [R02-F03](annotations/R02.json) | [SKILL.md:63-69](inputs/upstream/playwright/SKILL.md#L63) |
| actual_behavior | R03 | [R03-F03](annotations/R03.json) | [SKILL.md:35-38](inputs/upstream/gh-fix-ci/SKILL.md#L35); [SKILL.md:60-69](inputs/upstream/gh-fix-ci/SKILL.md#L60) |
| actual_behavior | R04 | [R04-F05](annotations/R04.json) | [SKILL.md:106-116](inputs/upstream/netlify-deploy/SKILL.md#L106); [SKILL.md:138-150](inputs/upstream/netlify-deploy/SKILL.md#L138) |
| actual_behavior | R05 | [R05-F07](annotations/R05.json) | [SKILL.md:43-44](inputs/upstream/linear/SKILL.md#L43); [SKILL.md:63-73](inputs/upstream/linear/SKILL.md#L63) |
| actual_behavior | R05 | [R05-F10](annotations/R05.json) | [SKILL.md:82-87](inputs/upstream/linear/SKILL.md#L82) |
| actual_behavior | R06 | [R06-F01](annotations/R06.json) | [SKILL.md:11-16](inputs/upstream/transcribe/SKILL.md#L11) |
| additional_behavior | D01 | [D01-F07](annotations/D01.json) | [SKILL.md:14-14](inputs/controlled/D01/SKILL.md#L14) |
| additional_behavior | D02 | [D02-F07](annotations/D02.json) | [SKILL.md:14-14](inputs/controlled/D02/SKILL.md#L14) |
| additional_behavior | D03 | [D03-F07](annotations/D03.json) | [SKILL.md:16-16](inputs/controlled/D03/SKILL.md#L16); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| additional_behavior | D04 | [D04-F07](annotations/D04.json) | [references/workflow.md:21-21](inputs/controlled/D04/references/workflow.md#L21); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8) |
| additional_behavior | D06 | [D06-F07](annotations/D06.json) | [SKILL.md:14-14](inputs/controlled/D06/SKILL.md#L14) |
| additional_behavior | F01 | [F01-F10](annotations/F01.json) | [SKILL.md:16-16](inputs/controlled/F01/SKILL.md#L16) |
| additional_behavior | F02 | [F02-F10](annotations/F02.json) | [SKILL.md:16-16](inputs/controlled/F02/SKILL.md#L16) |
| additional_behavior | F03 | [F03-F10](annotations/F03.json) | [SKILL.md:18-18](inputs/controlled/F03/SKILL.md#L18); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| additional_behavior | F04 | [F04-F10](annotations/F04.json) | [references/workflow.md:21-21](inputs/controlled/F04/references/workflow.md#L21); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| additional_behavior | F06 | [F06-F10](annotations/F06.json) | [SKILL.md:16-16](inputs/controlled/F06/SKILL.md#L16) |
| additional_behavior | N01 | [N01-F09](annotations/N01.json) | [SKILL.md:16-16](inputs/controlled/N01/SKILL.md#L16) |
| additional_behavior | N02 | [N02-F09](annotations/N02.json) | [SKILL.md:16-16](inputs/controlled/N02/SKILL.md#L16) |
| additional_behavior | N03 | [N03-F09](annotations/N03.json) | [SKILL.md:18-18](inputs/controlled/N03/SKILL.md#L18); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| additional_behavior | N04 | [N04-F09](annotations/N04.json) | [references/workflow.md:21-21](inputs/controlled/N04/references/workflow.md#L21); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8) |
| additional_behavior | N06 | [N06-F09](annotations/N06.json) | [SKILL.md:16-16](inputs/controlled/N06/SKILL.md#L16) |
| additional_behavior | Q01 | [Q01-F11](annotations/Q01.json) | [SKILL.md:17-17](inputs/controlled/Q01/SKILL.md#L17); [SKILL.md:18-18](inputs/controlled/Q01/SKILL.md#L18) |
| additional_behavior | Q02 | [Q02-F11](annotations/Q02.json) | [SKILL.md:16-16](inputs/controlled/Q02/SKILL.md#L16); [SKILL.md:18-18](inputs/controlled/Q02/SKILL.md#L18) |
| additional_behavior | Q03 | [Q03-F11](annotations/Q03.json) | [SKILL.md:23-23](inputs/controlled/Q03/SKILL.md#L23); [SKILL.md:25-25](inputs/controlled/Q03/SKILL.md#L25) |
| additional_behavior | Q04 | [Q04-F11](annotations/Q04.json) | [references/workflow.md:21-21](inputs/controlled/Q04/references/workflow.md#L21); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8); [references/workflow.md:23-23](inputs/controlled/Q04/references/workflow.md#L23) |
| additional_behavior | Q06 | [Q06-F11](annotations/Q06.json) | [SKILL.md:17-17](inputs/controlled/Q06/SKILL.md#L17); [SKILL.md:18-18](inputs/controlled/Q06/SKILL.md#L18) |
| adopted_example | D01 | [D01-F05](annotations/D01.json) | [SKILL.md:12-12](inputs/controlled/D01/SKILL.md#L12); [SKILL.md:21-23](inputs/controlled/D01/SKILL.md#L21); [scripts/package.py:7-13](inputs/controlled/D01/scripts/package.py#L7) |
| adopted_example | D02 | [D02-F05](annotations/D02.json) | [SKILL.md:12-12](inputs/controlled/D02/SKILL.md#L12); [SKILL.md:20-22](inputs/controlled/D02/SKILL.md#L20); [scripts/package.py:7-13](inputs/controlled/D02/scripts/package.py#L7) |
| adopted_example | D03 | [D03-F05](annotations/D03.json) | [SKILL.md:14-14](inputs/controlled/D03/SKILL.md#L14); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [SKILL.md:23-25](inputs/controlled/D03/SKILL.md#L23); [scripts/package.py:7-13](inputs/controlled/D03/scripts/package.py#L7) |
| adopted_example | D04 | [D04-F05](annotations/D04.json) | [references/workflow.md:11-11](inputs/controlled/D04/references/workflow.md#L11); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8); [references/workflow.md:15-17](inputs/controlled/D04/references/workflow.md#L15); [scripts/package.py:7-13](inputs/controlled/D04/scripts/package.py#L7) |
| adopted_example | D05 | [D05-F05](annotations/D05.json) | [SKILL.md:12-12](inputs/controlled/D05/SKILL.md#L12); [SKILL.md:21-23](inputs/controlled/D05/SKILL.md#L21); [scripts/package.py:7-13](inputs/controlled/D05/scripts/package.py#L7) |
| adopted_example | D06 | [D06-F05](annotations/D06.json) | [SKILL.md:12-12](inputs/controlled/D06/SKILL.md#L12); [SKILL.md:21-23](inputs/controlled/D06/SKILL.md#L21); [scripts/package.py:7-13](inputs/controlled/D06/scripts/package.py#L7) |
| adopted_reference | R04 | [R04-F03](annotations/R04.json) | [SKILL.md:243-247](inputs/upstream/netlify-deploy/SKILL.md#L243); [references/deployment-patterns.md:5-19](inputs/upstream/netlify-deploy/references/deployment-patterns.md#L5) |
| adopted_reference | R05 | [R05-F07](annotations/R05.json) | [SKILL.md:43-44](inputs/upstream/linear/SKILL.md#L43); [SKILL.md:63-73](inputs/upstream/linear/SKILL.md#L63) |
| black_box | D01 | [D01-F02](annotations/D01.json) | [SKILL.md:9-9](inputs/controlled/D01/SKILL.md#L9); [scripts/convert.py:5-10](inputs/controlled/D01/scripts/convert.py#L5) |
| black_box | D01 | [D01-F04](annotations/D01.json) | [SKILL.md:9-9](inputs/controlled/D01/SKILL.md#L9); [SKILL.md:11-11](inputs/controlled/D01/SKILL.md#L11); [scripts/convert.py:5-10](inputs/controlled/D01/scripts/convert.py#L5) |
| black_box | D01 | [D01-F05](annotations/D01.json) | [SKILL.md:12-12](inputs/controlled/D01/SKILL.md#L12); [SKILL.md:21-23](inputs/controlled/D01/SKILL.md#L21); [scripts/package.py:7-13](inputs/controlled/D01/scripts/package.py#L7) |
| black_box | D02 | [D02-F02](annotations/D02.json) | [SKILL.md:8-8](inputs/controlled/D02/SKILL.md#L8); [scripts/convert.py:5-10](inputs/controlled/D02/scripts/convert.py#L5) |
| black_box | D02 | [D02-F04](annotations/D02.json) | [SKILL.md:8-8](inputs/controlled/D02/SKILL.md#L8); [SKILL.md:10-10](inputs/controlled/D02/SKILL.md#L10); [scripts/convert.py:5-10](inputs/controlled/D02/scripts/convert.py#L5) |
| black_box | D02 | [D02-F05](annotations/D02.json) | [SKILL.md:12-12](inputs/controlled/D02/SKILL.md#L12); [SKILL.md:20-22](inputs/controlled/D02/SKILL.md#L20); [scripts/package.py:7-13](inputs/controlled/D02/scripts/package.py#L7) |
| black_box | D03 | [D03-F02](annotations/D03.json) | [SKILL.md:11-11](inputs/controlled/D03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [scripts/convert.py:5-10](inputs/controlled/D03/scripts/convert.py#L5) |
| black_box | D03 | [D03-F04](annotations/D03.json) | [SKILL.md:11-11](inputs/controlled/D03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [SKILL.md:13-13](inputs/controlled/D03/SKILL.md#L13); [scripts/convert.py:5-10](inputs/controlled/D03/scripts/convert.py#L5) |
| black_box | D03 | [D03-F05](annotations/D03.json) | [SKILL.md:14-14](inputs/controlled/D03/SKILL.md#L14); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [SKILL.md:23-25](inputs/controlled/D03/SKILL.md#L23); [scripts/package.py:7-13](inputs/controlled/D03/scripts/package.py#L7) |
| black_box | D04 | [D04-F02](annotations/D04.json) | [references/workflow.md:6-6](inputs/controlled/D04/references/workflow.md#L6); [references/workflow.md:5-5](inputs/controlled/D04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8); [scripts/convert.py:5-10](inputs/controlled/D04/scripts/convert.py#L5) |
| black_box | D04 | [D04-F04](annotations/D04.json) | [references/workflow.md:6-6](inputs/controlled/D04/references/workflow.md#L6); [references/workflow.md:5-5](inputs/controlled/D04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8); [references/workflow.md:9-9](inputs/controlled/D04/references/workflow.md#L9); [scripts/convert.py:5-10](inputs/controlled/D04/scripts/convert.py#L5) |
| black_box | D04 | [D04-F05](annotations/D04.json) | [references/workflow.md:11-11](inputs/controlled/D04/references/workflow.md#L11); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8); [references/workflow.md:15-17](inputs/controlled/D04/references/workflow.md#L15); [scripts/package.py:7-13](inputs/controlled/D04/scripts/package.py#L7) |
| black_box | D05 | [D05-F02](annotations/D05.json) | [SKILL.md:9-9](inputs/controlled/D05/SKILL.md#L9); [scripts/convert.py:5-10](inputs/controlled/D05/scripts/convert.py#L5) |
| black_box | D05 | [D05-F04](annotations/D05.json) | [SKILL.md:9-9](inputs/controlled/D05/SKILL.md#L9); [SKILL.md:11-11](inputs/controlled/D05/SKILL.md#L11); [scripts/convert.py:5-10](inputs/controlled/D05/scripts/convert.py#L5) |
| black_box | D05 | [D05-F05](annotations/D05.json) | [SKILL.md:12-12](inputs/controlled/D05/SKILL.md#L12); [SKILL.md:21-23](inputs/controlled/D05/SKILL.md#L21); [scripts/package.py:7-13](inputs/controlled/D05/scripts/package.py#L7) |
| black_box | D06 | [D06-F02](annotations/D06.json) | [SKILL.md:9-9](inputs/controlled/D06/SKILL.md#L9); [scripts/convert.py:5-10](inputs/controlled/D06/scripts/convert.py#L5) |
| black_box | D06 | [D06-F04](annotations/D06.json) | [SKILL.md:9-9](inputs/controlled/D06/SKILL.md#L9); [SKILL.md:11-11](inputs/controlled/D06/SKILL.md#L11); [scripts/convert.py:5-10](inputs/controlled/D06/scripts/convert.py#L5) |
| black_box | D06 | [D06-F05](annotations/D06.json) | [SKILL.md:12-12](inputs/controlled/D06/SKILL.md#L12); [SKILL.md:21-23](inputs/controlled/D06/SKILL.md#L21); [scripts/package.py:7-13](inputs/controlled/D06/scripts/package.py#L7) |
| blockquote | D04 | [D04-F04](annotations/D04.json) | [references/workflow.md:6-6](inputs/controlled/D04/references/workflow.md#L6); [references/workflow.md:5-5](inputs/controlled/D04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8); [references/workflow.md:9-9](inputs/controlled/D04/references/workflow.md#L9); [scripts/convert.py:5-10](inputs/controlled/D04/scripts/convert.py#L5) |
| blockquote | D04 | [D04-F08](annotations/D04.json) | [references/workflow.md:23-23](inputs/controlled/D04/references/workflow.md#L23); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8) |
| blockquote | D04 | [D04-F09](annotations/D04.json) | [references/workflow.md:25-25](inputs/controlled/D04/references/workflow.md#L25); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8) |
| blockquote | F04 | [F04-F09](annotations/F04.json) | [references/workflow.md:19-19](inputs/controlled/F04/references/workflow.md#L19); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| blockquote | N04 | [N04-F07](annotations/N04.json) | [references/workflow.md:17-17](inputs/controlled/N04/references/workflow.md#L17); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8) |
| blockquote | Q04 | [Q04-F09](annotations/Q04.json) | [references/workflow.md:3-3](inputs/controlled/Q04/references/workflow.md#L3); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8) |
| capability_description | Q01 | [Q01-F09](annotations/Q01.json) | [SKILL.md:8-8](inputs/controlled/Q01/SKILL.md#L8) |
| capability_description | Q02 | [Q02-F09](annotations/Q02.json) | [SKILL.md:8-8](inputs/controlled/Q02/SKILL.md#L8) |
| capability_description | Q03 | [Q03-F09](annotations/Q03.json) | [SKILL.md:8-8](inputs/controlled/Q03/SKILL.md#L8) |
| capability_description | Q04 | [Q04-F09](annotations/Q04.json) | [references/workflow.md:3-3](inputs/controlled/Q04/references/workflow.md#L3); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8) |
| capability_description | Q05 | [Q05-F09](annotations/Q05.json) | [SKILL.md:8-8](inputs/controlled/Q05/SKILL.md#L8) |
| capability_description | Q06 | [Q06-F09](annotations/Q06.json) | [SKILL.md:8-8](inputs/controlled/Q06/SKILL.md#L8) |
| capability_vs_execution | R02 | [R02-F07](annotations/R02.json) | [SKILL.md:132-137](inputs/upstream/playwright/SKILL.md#L132); [references/cli.md:19-49](inputs/upstream/playwright/references/cli.md#L19) |
| capability_vs_execution | R04 | [R04-F06](annotations/R04.json) | [SKILL.md:152-163](inputs/upstream/netlify-deploy/SKILL.md#L152); [SKILL.md:243-247](inputs/upstream/netlify-deploy/SKILL.md#L243); [references/netlify-toml.md:13-33](inputs/upstream/netlify-deploy/references/netlify-toml.md#L13) |
| capability_vs_execution | R04 | [R04-F09](annotations/R04.json) | [SKILL.md:223-229](inputs/upstream/netlify-deploy/SKILL.md#L223); [SKILL.md:243-247](inputs/upstream/netlify-deploy/SKILL.md#L243); [references/cli-commands.md:82-96](inputs/upstream/netlify-deploy/references/cli-commands.md#L82) |
| capability_vs_execution | R05 | [R05-F06](annotations/R05.json) | [SKILL.md:43-44](inputs/upstream/linear/SKILL.md#L43); [SKILL.md:55-61](inputs/upstream/linear/SKILL.md#L55) |
| capability_vs_execution | R06 | [R06-F09](annotations/R06.json) | [SKILL.md:80-81](inputs/upstream/transcribe/SKILL.md#L80); [references/api.md:3-6](inputs/upstream/transcribe/references/api.md#L3); [scripts/transcribe_diarize.py:18-19](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L18); [scripts/transcribe_diarize.py:145-152](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L145) |
| code_block | D01 | [D01-F05](annotations/D01.json) | [SKILL.md:12-12](inputs/controlled/D01/SKILL.md#L12); [SKILL.md:21-23](inputs/controlled/D01/SKILL.md#L21); [scripts/package.py:7-13](inputs/controlled/D01/scripts/package.py#L7) |
| code_block | D02 | [D02-F05](annotations/D02.json) | [SKILL.md:12-12](inputs/controlled/D02/SKILL.md#L12); [SKILL.md:20-22](inputs/controlled/D02/SKILL.md#L20); [scripts/package.py:7-13](inputs/controlled/D02/scripts/package.py#L7) |
| code_block | D03 | [D03-F05](annotations/D03.json) | [SKILL.md:14-14](inputs/controlled/D03/SKILL.md#L14); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [SKILL.md:23-25](inputs/controlled/D03/SKILL.md#L23); [scripts/package.py:7-13](inputs/controlled/D03/scripts/package.py#L7) |
| code_block | D04 | [D04-F05](annotations/D04.json) | [references/workflow.md:11-11](inputs/controlled/D04/references/workflow.md#L11); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8); [references/workflow.md:15-17](inputs/controlled/D04/references/workflow.md#L15); [scripts/package.py:7-13](inputs/controlled/D04/scripts/package.py#L7) |
| code_block | D05 | [D05-F05](annotations/D05.json) | [SKILL.md:12-12](inputs/controlled/D05/SKILL.md#L12); [SKILL.md:21-23](inputs/controlled/D05/SKILL.md#L21); [scripts/package.py:7-13](inputs/controlled/D05/scripts/package.py#L7) |
| code_block | D06 | [D06-F05](annotations/D06.json) | [SKILL.md:12-12](inputs/controlled/D06/SKILL.md#L12); [SKILL.md:21-23](inputs/controlled/D06/SKILL.md#L21); [scripts/package.py:7-13](inputs/controlled/D06/scripts/package.py#L7) |
| code_block | R01 | [R01-F04](annotations/R01.json) | [SKILL.md:15-17](inputs/upstream/pdf/SKILL.md#L15); [SKILL.md:52-55](inputs/upstream/pdf/SKILL.md#L52) |
| code_block | R01 | [R01-F07](annotations/R01.json) | [SKILL.md:27-45](inputs/upstream/pdf/SKILL.md#L27) |
| code_block | R02 | [R02-F02](annotations/R02.json) | [SKILL.md:12-32](inputs/upstream/playwright/SKILL.md#L12) |
| code_boundary | R02 | [R02-F06](annotations/R02.json) | [SKILL.md:124-130](inputs/upstream/playwright/SKILL.md#L124); [scripts/playwright_cli.sh:9-25](inputs/upstream/playwright/scripts/playwright_cli.sh#L9) |
| code_boundary | R03 | [R03-F03](annotations/R03.json) | [SKILL.md:35-38](inputs/upstream/gh-fix-ci/SKILL.md#L35); [SKILL.md:60-69](inputs/upstream/gh-fix-ci/SKILL.md#L60) |
| code_boundary | R06 | [R06-F06](annotations/R06.json) | [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:155-186](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L155) |
| code_boundary | R06 | [R06-F11](annotations/R06.json) | [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:169-186](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L169); [scripts/transcribe_diarize.py:252-264](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L252) |
| condition_preservation | R01 | [R01-F02](annotations/R01.json) | [SKILL.md:14-20](inputs/upstream/pdf/SKILL.md#L14); [SKILL.md:47-47](inputs/upstream/pdf/SKILL.md#L47) |
| condition_preservation | R01 | [R01-F05](annotations/R01.json) | [SKILL.md:20-20](inputs/upstream/pdf/SKILL.md#L20); [SKILL.md:64-66](inputs/upstream/pdf/SKILL.md#L64) |
| condition_preservation | R02 | [R02-F03](annotations/R02.json) | [SKILL.md:63-69](inputs/upstream/playwright/SKILL.md#L63) |
| condition_preservation | R03 | [R03-F01](annotations/R03.json) | [SKILL.md:29-31](inputs/upstream/gh-fix-ci/SKILL.md#L29) |
| condition_preservation | R03 | [R03-F05](annotations/R03.json) | [SKILL.md:42-46](inputs/upstream/gh-fix-ci/SKILL.md#L42); [scripts/inspect_pr_checks.py:333-355](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L333); [scripts/inspect_pr_checks.py:366-377](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L366) |
| condition_preservation | R03 | [R03-F07](annotations/R03.json) | [SKILL.md:50-58](inputs/upstream/gh-fix-ci/SKILL.md#L50) |
| condition_preservation | R04 | [R04-F02](annotations/R04.json) | [SKILL.md:70-98](inputs/upstream/netlify-deploy/SKILL.md#L70) |
| condition_preservation | R04 | [R04-F07](annotations/R04.json) | [SKILL.md:192-209](inputs/upstream/netlify-deploy/SKILL.md#L192) |
| condition_preservation | R05 | [R05-F02](annotations/R05.json) | [SKILL.md:22-33](inputs/upstream/linear/SKILL.md#L22) |
| condition_preservation | R05 | [R05-F07](annotations/R05.json) | [SKILL.md:43-44](inputs/upstream/linear/SKILL.md#L43); [SKILL.md:63-73](inputs/upstream/linear/SKILL.md#L63) |
| condition_preservation | R05 | [R05-F10](annotations/R05.json) | [SKILL.md:82-87](inputs/upstream/linear/SKILL.md#L82) |
| condition_preservation | R06 | [R06-F01](annotations/R06.json) | [SKILL.md:11-16](inputs/upstream/transcribe/SKILL.md#L11) |
| condition_preservation | R06 | [R06-F03](annotations/R06.json) | [SKILL.md:18-22](inputs/upstream/transcribe/SKILL.md#L18) |
| condition_preservation | R06 | [R06-F07](annotations/R06.json) | [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:33-40](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L33); [scripts/transcribe_diarize.py:246-264](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L246) |
| condition_preservation | R06 | [R06-F11](annotations/R06.json) | [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:169-186](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L169); [scripts/transcribe_diarize.py:252-264](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L252) |
| conditional_instruction | R01 | [R01-F07](annotations/R01.json) | [SKILL.md:27-45](inputs/upstream/pdf/SKILL.md#L27) |
| conditional_instruction | R04 | [R04-F03](annotations/R04.json) | [SKILL.md:243-247](inputs/upstream/netlify-deploy/SKILL.md#L243); [references/deployment-patterns.md:5-19](inputs/upstream/netlify-deploy/references/deployment-patterns.md#L5) |
| conditional_instruction | R04 | [R04-F08](annotations/R04.json) | [SKILL.md:213-220](inputs/upstream/netlify-deploy/SKILL.md#L213) |
| conditional_instruction | R05 | [R05-F03](annotations/R05.json) | [SKILL.md:35-38](inputs/upstream/linear/SKILL.md#L35) |
| conditional_instruction | R05 | [R05-F10](annotations/R05.json) | [SKILL.md:82-87](inputs/upstream/linear/SKILL.md#L82) |
| configuration_snippet | R02 | [R02-F09](annotations/R02.json) | [SKILL.md:132-137](inputs/upstream/playwright/SKILL.md#L132); [references/workflows.md:72-89](inputs/upstream/playwright/references/workflows.md#L72) |
| configuration_snippet | R04 | [R04-F06](annotations/R04.json) | [SKILL.md:152-163](inputs/upstream/netlify-deploy/SKILL.md#L152); [SKILL.md:243-247](inputs/upstream/netlify-deploy/SKILL.md#L243); [references/netlify-toml.md:13-33](inputs/upstream/netlify-deploy/references/netlify-toml.md#L13) |
| configuration_snippet | R05 | [R05-F03](annotations/R05.json) | [SKILL.md:35-38](inputs/upstream/linear/SKILL.md#L35) |
| configuration_snippet | R05 | [R05-F09](annotations/R05.json) | [SKILL.md:14-16](inputs/upstream/linear/SKILL.md#L14); [agents/openai.yaml:1-14](inputs/upstream/linear/agents/openai.yaml#L1) |
| control_flow_order | R05 | [R05-F01](annotations/R05.json) | [SKILL.md:14-20](inputs/upstream/linear/SKILL.md#L14) |
| control_flow_order | R05 | [R05-F04](annotations/R05.json) | [SKILL.md:40-50](inputs/upstream/linear/SKILL.md#L40) |
| cross_file | D01 | [D01-F02](annotations/D01.json) | [SKILL.md:9-9](inputs/controlled/D01/SKILL.md#L9); [scripts/convert.py:5-10](inputs/controlled/D01/scripts/convert.py#L5) |
| cross_file | D01 | [D01-F04](annotations/D01.json) | [SKILL.md:9-9](inputs/controlled/D01/SKILL.md#L9); [SKILL.md:11-11](inputs/controlled/D01/SKILL.md#L11); [scripts/convert.py:5-10](inputs/controlled/D01/scripts/convert.py#L5) |
| cross_file | D01 | [D01-F05](annotations/D01.json) | [SKILL.md:12-12](inputs/controlled/D01/SKILL.md#L12); [SKILL.md:21-23](inputs/controlled/D01/SKILL.md#L21); [scripts/package.py:7-13](inputs/controlled/D01/scripts/package.py#L7) |
| cross_file | D02 | [D02-F02](annotations/D02.json) | [SKILL.md:8-8](inputs/controlled/D02/SKILL.md#L8); [scripts/convert.py:5-10](inputs/controlled/D02/scripts/convert.py#L5) |
| cross_file | D02 | [D02-F04](annotations/D02.json) | [SKILL.md:8-8](inputs/controlled/D02/SKILL.md#L8); [SKILL.md:10-10](inputs/controlled/D02/SKILL.md#L10); [scripts/convert.py:5-10](inputs/controlled/D02/scripts/convert.py#L5) |
| cross_file | D02 | [D02-F05](annotations/D02.json) | [SKILL.md:12-12](inputs/controlled/D02/SKILL.md#L12); [SKILL.md:20-22](inputs/controlled/D02/SKILL.md#L20); [scripts/package.py:7-13](inputs/controlled/D02/scripts/package.py#L7) |
| cross_file | D03 | [D03-F02](annotations/D03.json) | [SKILL.md:11-11](inputs/controlled/D03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [scripts/convert.py:5-10](inputs/controlled/D03/scripts/convert.py#L5) |
| cross_file | D03 | [D03-F04](annotations/D03.json) | [SKILL.md:11-11](inputs/controlled/D03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [SKILL.md:13-13](inputs/controlled/D03/SKILL.md#L13); [scripts/convert.py:5-10](inputs/controlled/D03/scripts/convert.py#L5) |
| cross_file | D03 | [D03-F05](annotations/D03.json) | [SKILL.md:14-14](inputs/controlled/D03/SKILL.md#L14); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [SKILL.md:23-25](inputs/controlled/D03/SKILL.md#L23); [scripts/package.py:7-13](inputs/controlled/D03/scripts/package.py#L7) |
| cross_file | D04 | [D04-F01](annotations/D04.json) | [references/workflow.md:3-3](inputs/controlled/D04/references/workflow.md#L3); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8) |
| cross_file | D04 | [D04-F02](annotations/D04.json) | [references/workflow.md:6-6](inputs/controlled/D04/references/workflow.md#L6); [references/workflow.md:5-5](inputs/controlled/D04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8); [scripts/convert.py:5-10](inputs/controlled/D04/scripts/convert.py#L5) |
| cross_file | D04 | [D04-F03](annotations/D04.json) | [references/workflow.md:7-7](inputs/controlled/D04/references/workflow.md#L7); [references/workflow.md:5-5](inputs/controlled/D04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8) |
| cross_file | D04 | [D04-F04](annotations/D04.json) | [references/workflow.md:6-6](inputs/controlled/D04/references/workflow.md#L6); [references/workflow.md:5-5](inputs/controlled/D04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8); [references/workflow.md:9-9](inputs/controlled/D04/references/workflow.md#L9); [scripts/convert.py:5-10](inputs/controlled/D04/scripts/convert.py#L5) |
| cross_file | D04 | [D04-F05](annotations/D04.json) | [references/workflow.md:11-11](inputs/controlled/D04/references/workflow.md#L11); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8); [references/workflow.md:15-17](inputs/controlled/D04/references/workflow.md#L15); [scripts/package.py:7-13](inputs/controlled/D04/scripts/package.py#L7) |
| cross_file | D04 | [D04-F06](annotations/D04.json) | [references/workflow.md:3-3](inputs/controlled/D04/references/workflow.md#L3); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8); [references/workflow.md:19-19](inputs/controlled/D04/references/workflow.md#L19) |
| cross_file | D04 | [D04-F07](annotations/D04.json) | [references/workflow.md:21-21](inputs/controlled/D04/references/workflow.md#L21); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8) |
| cross_file | D04 | [D04-F08](annotations/D04.json) | [references/workflow.md:23-23](inputs/controlled/D04/references/workflow.md#L23); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8) |
| cross_file | D04 | [D04-F09](annotations/D04.json) | [references/workflow.md:25-25](inputs/controlled/D04/references/workflow.md#L25); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8) |
| cross_file | D04 | [D04-F10](annotations/D04.json) | [references/workflow.md:27-27](inputs/controlled/D04/references/workflow.md#L27); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8) |
| cross_file | D05 | [D05-F02](annotations/D05.json) | [SKILL.md:9-9](inputs/controlled/D05/SKILL.md#L9); [scripts/convert.py:5-10](inputs/controlled/D05/scripts/convert.py#L5) |
| cross_file | D05 | [D05-F04](annotations/D05.json) | [SKILL.md:9-9](inputs/controlled/D05/SKILL.md#L9); [SKILL.md:11-11](inputs/controlled/D05/SKILL.md#L11); [scripts/convert.py:5-10](inputs/controlled/D05/scripts/convert.py#L5) |
| cross_file | D05 | [D05-F05](annotations/D05.json) | [SKILL.md:12-12](inputs/controlled/D05/SKILL.md#L12); [SKILL.md:21-23](inputs/controlled/D05/SKILL.md#L21); [scripts/package.py:7-13](inputs/controlled/D05/scripts/package.py#L7) |
| cross_file | D06 | [D06-F02](annotations/D06.json) | [SKILL.md:9-9](inputs/controlled/D06/SKILL.md#L9); [scripts/convert.py:5-10](inputs/controlled/D06/scripts/convert.py#L5) |
| cross_file | D06 | [D06-F04](annotations/D06.json) | [SKILL.md:9-9](inputs/controlled/D06/SKILL.md#L9); [SKILL.md:11-11](inputs/controlled/D06/SKILL.md#L11); [scripts/convert.py:5-10](inputs/controlled/D06/scripts/convert.py#L5) |
| cross_file | D06 | [D06-F05](annotations/D06.json) | [SKILL.md:12-12](inputs/controlled/D06/SKILL.md#L12); [SKILL.md:21-23](inputs/controlled/D06/SKILL.md#L21); [scripts/package.py:7-13](inputs/controlled/D06/scripts/package.py#L7) |
| cross_file | F04 | [F04-F01](annotations/F04.json) | [references/workflow.md:3-3](inputs/controlled/F04/references/workflow.md#L3); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| cross_file | F04 | [F04-F02](annotations/F04.json) | [references/workflow.md:5-5](inputs/controlled/F04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| cross_file | F04 | [F04-F03](annotations/F04.json) | [references/workflow.md:3-3](inputs/controlled/F04/references/workflow.md#L3); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8); [references/workflow.md:5-5](inputs/controlled/F04/references/workflow.md#L5) |
| cross_file | F04 | [F04-F04](annotations/F04.json) | [references/workflow.md:8-8](inputs/controlled/F04/references/workflow.md#L8); [references/workflow.md:7-7](inputs/controlled/F04/references/workflow.md#L7); [references/workflow.md:11-11](inputs/controlled/F04/references/workflow.md#L11); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8); [retry.yaml:1-3](inputs/controlled/F04/retry.yaml#L1) |
| cross_file | F04 | [F04-F05](annotations/F04.json) | [references/workflow.md:9-9](inputs/controlled/F04/references/workflow.md#L9); [references/workflow.md:7-7](inputs/controlled/F04/references/workflow.md#L7); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| cross_file | F04 | [F04-F06](annotations/F04.json) | [references/workflow.md:13-13](inputs/controlled/F04/references/workflow.md#L13); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| cross_file | F04 | [F04-F07](annotations/F04.json) | [references/workflow.md:15-15](inputs/controlled/F04/references/workflow.md#L15); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| cross_file | F04 | [F04-F08](annotations/F04.json) | [references/workflow.md:17-17](inputs/controlled/F04/references/workflow.md#L17); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| cross_file | F04 | [F04-F09](annotations/F04.json) | [references/workflow.md:19-19](inputs/controlled/F04/references/workflow.md#L19); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| cross_file | F04 | [F04-F10](annotations/F04.json) | [references/workflow.md:21-21](inputs/controlled/F04/references/workflow.md#L21); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| cross_file | N04 | [N04-F01](annotations/N04.json) | [references/workflow.md:3-3](inputs/controlled/N04/references/workflow.md#L3); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8) |
| cross_file | N04 | [N04-F02](annotations/N04.json) | [references/workflow.md:6-6](inputs/controlled/N04/references/workflow.md#L6); [references/workflow.md:5-5](inputs/controlled/N04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8); [references/workflow.md:7-7](inputs/controlled/N04/references/workflow.md#L7) |
| cross_file | N04 | [N04-F03](annotations/N04.json) | [references/workflow.md:6-6](inputs/controlled/N04/references/workflow.md#L6); [references/workflow.md:5-5](inputs/controlled/N04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8); [references/workflow.md:7-7](inputs/controlled/N04/references/workflow.md#L7) |
| cross_file | N04 | [N04-F04](annotations/N04.json) | [references/workflow.md:9-9](inputs/controlled/N04/references/workflow.md#L9); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8) |
| cross_file | N04 | [N04-F05](annotations/N04.json) | [references/workflow.md:11-11](inputs/controlled/N04/references/workflow.md#L11); [references/workflow.md:13-13](inputs/controlled/N04/references/workflow.md#L13); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8); [payload.json:1-3](inputs/controlled/N04/payload.json#L1) |
| cross_file | N04 | [N04-F06](annotations/N04.json) | [references/workflow.md:15-15](inputs/controlled/N04/references/workflow.md#L15); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8) |
| cross_file | N04 | [N04-F07](annotations/N04.json) | [references/workflow.md:17-17](inputs/controlled/N04/references/workflow.md#L17); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8) |
| cross_file | N04 | [N04-F08](annotations/N04.json) | [references/workflow.md:19-19](inputs/controlled/N04/references/workflow.md#L19); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8) |
| cross_file | N04 | [N04-F09](annotations/N04.json) | [references/workflow.md:21-21](inputs/controlled/N04/references/workflow.md#L21); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8) |
| cross_file | Q04 | [Q04-F01](annotations/Q04.json) | [references/workflow.md:5-5](inputs/controlled/Q04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8) |
| cross_file | Q04 | [Q04-F02](annotations/Q04.json) | [references/workflow.md:7-7](inputs/controlled/Q04/references/workflow.md#L7); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8) |
| cross_file | Q04 | [Q04-F03](annotations/Q04.json) | [references/workflow.md:10-10](inputs/controlled/Q04/references/workflow.md#L10); [references/workflow.md:9-9](inputs/controlled/Q04/references/workflow.md#L9); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8) |
| cross_file | Q04 | [Q04-F04](annotations/Q04.json) | [references/workflow.md:11-11](inputs/controlled/Q04/references/workflow.md#L11); [references/workflow.md:9-9](inputs/controlled/Q04/references/workflow.md#L9); [references/workflow.md:15-15](inputs/controlled/Q04/references/workflow.md#L15); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8); [query.yaml:2-2](inputs/controlled/Q04/query.yaml#L2); [query.yaml:1-1](inputs/controlled/Q04/query.yaml#L1) |
| cross_file | Q04 | [Q04-F05](annotations/Q04.json) | [references/workflow.md:12-12](inputs/controlled/Q04/references/workflow.md#L12); [references/workflow.md:9-9](inputs/controlled/Q04/references/workflow.md#L9); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8) |
| cross_file | Q04 | [Q04-F06](annotations/Q04.json) | [references/workflow.md:13-13](inputs/controlled/Q04/references/workflow.md#L13); [references/workflow.md:9-9](inputs/controlled/Q04/references/workflow.md#L9); [references/workflow.md:15-15](inputs/controlled/Q04/references/workflow.md#L15); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8); [query.yaml:3-3](inputs/controlled/Q04/query.yaml#L3); [query.yaml:1-1](inputs/controlled/Q04/query.yaml#L1) |
| cross_file | Q04 | [Q04-F07](annotations/Q04.json) | [references/workflow.md:23-23](inputs/controlled/Q04/references/workflow.md#L23); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8) |
| cross_file | Q04 | [Q04-F08](annotations/Q04.json) | [references/workflow.md:17-17](inputs/controlled/Q04/references/workflow.md#L17); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8) |
| cross_file | Q04 | [Q04-F09](annotations/Q04.json) | [references/workflow.md:3-3](inputs/controlled/Q04/references/workflow.md#L3); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8) |
| cross_file | Q04 | [Q04-F10](annotations/Q04.json) | [references/workflow.md:10-10](inputs/controlled/Q04/references/workflow.md#L10); [references/workflow.md:9-9](inputs/controlled/Q04/references/workflow.md#L9); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8); [references/workflow.md:19-19](inputs/controlled/Q04/references/workflow.md#L19) |
| cross_file | Q04 | [Q04-F11](annotations/Q04.json) | [references/workflow.md:21-21](inputs/controlled/Q04/references/workflow.md#L21); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8); [references/workflow.md:23-23](inputs/controlled/Q04/references/workflow.md#L23) |
| cross_file_reference | R02 | [R02-F04](annotations/R02.json) | [SKILL.md:80-89](inputs/upstream/playwright/SKILL.md#L80); [SKILL.md:132-137](inputs/upstream/playwright/SKILL.md#L132); [references/workflows.md:91-95](inputs/upstream/playwright/references/workflows.md#L91) |
| cross_file_reference | R02 | [R02-F06](annotations/R02.json) | [SKILL.md:124-130](inputs/upstream/playwright/SKILL.md#L124); [scripts/playwright_cli.sh:9-25](inputs/upstream/playwright/scripts/playwright_cli.sh#L9) |
| cross_file_reference | R02 | [R02-F07](annotations/R02.json) | [SKILL.md:132-137](inputs/upstream/playwright/SKILL.md#L132); [references/cli.md:19-49](inputs/upstream/playwright/references/cli.md#L19) |
| cross_file_reference | R02 | [R02-F08](annotations/R02.json) | [SKILL.md:146-146](inputs/upstream/playwright/SKILL.md#L146); [SKILL.md:132-137](inputs/upstream/playwright/SKILL.md#L132); [references/workflows.md:3-5](inputs/upstream/playwright/references/workflows.md#L3) |
| cross_file_reference | R03 | [R03-F03](annotations/R03.json) | [SKILL.md:35-38](inputs/upstream/gh-fix-ci/SKILL.md#L35); [SKILL.md:60-69](inputs/upstream/gh-fix-ci/SKILL.md#L60) |
| cross_file_reference | R03 | [R03-F04](annotations/R03.json) | [SKILL.md:39-44](inputs/upstream/gh-fix-ci/SKILL.md#L39); [scripts/inspect_pr_checks.py:182-215](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L182) |
| cross_file_reference | R03 | [R03-F05](annotations/R03.json) | [SKILL.md:42-46](inputs/upstream/gh-fix-ci/SKILL.md#L42); [scripts/inspect_pr_checks.py:333-355](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L333); [scripts/inspect_pr_checks.py:366-377](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L366) |
| cross_file_reference | R03 | [R03-F09](annotations/R03.json) | [SKILL.md:64-64](inputs/upstream/gh-fix-ci/SKILL.md#L64); [scripts/inspect_pr_checks.py:110-135](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L110) |
| cross_file_reference | R04 | [R04-F03](annotations/R04.json) | [SKILL.md:243-247](inputs/upstream/netlify-deploy/SKILL.md#L243); [references/deployment-patterns.md:5-19](inputs/upstream/netlify-deploy/references/deployment-patterns.md#L5) |
| cross_file_reference | R04 | [R04-F04](annotations/R04.json) | [SKILL.md:118-136](inputs/upstream/netlify-deploy/SKILL.md#L118); [SKILL.md:243-247](inputs/upstream/netlify-deploy/SKILL.md#L243); [references/deployment-patterns.md:70-90](inputs/upstream/netlify-deploy/references/deployment-patterns.md#L70) |
| cross_file_reference | R04 | [R04-F10](annotations/R04.json) | [SKILL.md:238-247](inputs/upstream/netlify-deploy/SKILL.md#L238) |
| cross_file_reference | R06 | [R06-F04](annotations/R06.json) | [SKILL.md:22-22](inputs/upstream/transcribe/SKILL.md#L22); [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:241-244](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L241) |
| cross_file_reference | R06 | [R06-F05](annotations/R06.json) | [SKILL.md:61-70](inputs/upstream/transcribe/SKILL.md#L61); [SKILL.md:80-81](inputs/upstream/transcribe/SKILL.md#L80); [references/api.md:7-7](inputs/upstream/transcribe/references/api.md#L7); [scripts/transcribe_diarize.py:74-98](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L74); [scripts/transcribe_diarize.py:169-174](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L169) |
| cross_file_reference | R06 | [R06-F06](annotations/R06.json) | [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:155-186](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L155) |
| cross_file_reference | R06 | [R06-F07](annotations/R06.json) | [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:33-40](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L33); [scripts/transcribe_diarize.py:246-264](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L246) |
| cross_file_reference | R06 | [R06-F11](annotations/R06.json) | [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:169-186](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L169); [scripts/transcribe_diarize.py:252-264](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L252) |
| data_destination | R01 | [R01-F04](annotations/R01.json) | [SKILL.md:15-17](inputs/upstream/pdf/SKILL.md#L15); [SKILL.md:52-55](inputs/upstream/pdf/SKILL.md#L52) |
| data_destination | R02 | [R02-F03](annotations/R02.json) | [SKILL.md:63-69](inputs/upstream/playwright/SKILL.md#L63) |
| data_destination | R03 | [R03-F02](annotations/R03.json) | [SKILL.md:16-20](inputs/upstream/gh-fix-ci/SKILL.md#L16); [SKILL.md:32-38](inputs/upstream/gh-fix-ci/SKILL.md#L32) |
| data_destination | R03 | [R03-F05](annotations/R03.json) | [SKILL.md:42-46](inputs/upstream/gh-fix-ci/SKILL.md#L42); [scripts/inspect_pr_checks.py:333-355](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L333); [scripts/inspect_pr_checks.py:366-377](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L366) |
| data_destination | R03 | [R03-F07](annotations/R03.json) | [SKILL.md:50-58](inputs/upstream/gh-fix-ci/SKILL.md#L50) |
| data_destination | R04 | [R04-F02](annotations/R04.json) | [SKILL.md:70-98](inputs/upstream/netlify-deploy/SKILL.md#L70) |
| data_destination | R04 | [R04-F05](annotations/R04.json) | [SKILL.md:106-116](inputs/upstream/netlify-deploy/SKILL.md#L106); [SKILL.md:138-150](inputs/upstream/netlify-deploy/SKILL.md#L138) |
| data_destination | R05 | [R05-F04](annotations/R05.json) | [SKILL.md:40-50](inputs/upstream/linear/SKILL.md#L40) |
| data_destination | R05 | [R05-F08](annotations/R05.json) | [SKILL.md:52-53](inputs/upstream/linear/SKILL.md#L52); [SKILL.md:75-80](inputs/upstream/linear/SKILL.md#L75) |
| data_destination | R06 | [R06-F01](annotations/R06.json) | [SKILL.md:11-16](inputs/upstream/transcribe/SKILL.md#L11) |
| data_destination | R06 | [R06-F05](annotations/R06.json) | [SKILL.md:61-70](inputs/upstream/transcribe/SKILL.md#L61); [SKILL.md:80-81](inputs/upstream/transcribe/SKILL.md#L80); [references/api.md:7-7](inputs/upstream/transcribe/references/api.md#L7); [scripts/transcribe_diarize.py:74-98](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L74); [scripts/transcribe_diarize.py:169-174](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L169) |
| data_destination | R06 | [R06-F08](annotations/R06.json) | [SKILL.md:24-26](inputs/upstream/transcribe/SKILL.md#L24); [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:234-239](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L234); [scripts/transcribe_diarize.py:101-123](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L101); [scripts/transcribe_diarize.py:263-272](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L263) |
| data_flow | D01 | [D01-F01](annotations/D01.json) | [SKILL.md:8-8](inputs/controlled/D01/SKILL.md#L8) |
| data_flow | D01 | [D01-F02](annotations/D01.json) | [SKILL.md:9-9](inputs/controlled/D01/SKILL.md#L9); [scripts/convert.py:5-10](inputs/controlled/D01/scripts/convert.py#L5) |
| data_flow | D01 | [D01-F05](annotations/D01.json) | [SKILL.md:12-12](inputs/controlled/D01/SKILL.md#L12); [SKILL.md:21-23](inputs/controlled/D01/SKILL.md#L21); [scripts/package.py:7-13](inputs/controlled/D01/scripts/package.py#L7) |
| data_flow | D01 | [D01-F06](annotations/D01.json) | [SKILL.md:8-8](inputs/controlled/D01/SKILL.md#L8); [SKILL.md:13-13](inputs/controlled/D01/SKILL.md#L13) |
| data_flow | D02 | [D02-F01](annotations/D02.json) | [SKILL.md:8-8](inputs/controlled/D02/SKILL.md#L8) |
| data_flow | D02 | [D02-F02](annotations/D02.json) | [SKILL.md:8-8](inputs/controlled/D02/SKILL.md#L8); [scripts/convert.py:5-10](inputs/controlled/D02/scripts/convert.py#L5) |
| data_flow | D02 | [D02-F05](annotations/D02.json) | [SKILL.md:12-12](inputs/controlled/D02/SKILL.md#L12); [SKILL.md:20-22](inputs/controlled/D02/SKILL.md#L20); [scripts/package.py:7-13](inputs/controlled/D02/scripts/package.py#L7) |
| data_flow | D02 | [D02-F06](annotations/D02.json) | [SKILL.md:8-8](inputs/controlled/D02/SKILL.md#L8); [SKILL.md:12-12](inputs/controlled/D02/SKILL.md#L12) |
| data_flow | D03 | [D03-F01](annotations/D03.json) | [SKILL.md:10-10](inputs/controlled/D03/SKILL.md#L10); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| data_flow | D03 | [D03-F02](annotations/D03.json) | [SKILL.md:11-11](inputs/controlled/D03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [scripts/convert.py:5-10](inputs/controlled/D03/scripts/convert.py#L5) |
| data_flow | D03 | [D03-F05](annotations/D03.json) | [SKILL.md:14-14](inputs/controlled/D03/SKILL.md#L14); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [SKILL.md:23-25](inputs/controlled/D03/SKILL.md#L23); [scripts/package.py:7-13](inputs/controlled/D03/scripts/package.py#L7) |
| data_flow | D03 | [D03-F06](annotations/D03.json) | [SKILL.md:10-10](inputs/controlled/D03/SKILL.md#L10); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [SKILL.md:15-15](inputs/controlled/D03/SKILL.md#L15) |
| data_flow | D04 | [D04-F01](annotations/D04.json) | [references/workflow.md:3-3](inputs/controlled/D04/references/workflow.md#L3); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8) |
| data_flow | D04 | [D04-F02](annotations/D04.json) | [references/workflow.md:6-6](inputs/controlled/D04/references/workflow.md#L6); [references/workflow.md:5-5](inputs/controlled/D04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8); [scripts/convert.py:5-10](inputs/controlled/D04/scripts/convert.py#L5) |
| data_flow | D04 | [D04-F05](annotations/D04.json) | [references/workflow.md:11-11](inputs/controlled/D04/references/workflow.md#L11); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8); [references/workflow.md:15-17](inputs/controlled/D04/references/workflow.md#L15); [scripts/package.py:7-13](inputs/controlled/D04/scripts/package.py#L7) |
| data_flow | D04 | [D04-F06](annotations/D04.json) | [references/workflow.md:3-3](inputs/controlled/D04/references/workflow.md#L3); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8); [references/workflow.md:19-19](inputs/controlled/D04/references/workflow.md#L19) |
| data_flow | D05 | [D05-F01](annotations/D05.json) | [SKILL.md:8-8](inputs/controlled/D05/SKILL.md#L8) |
| data_flow | D05 | [D05-F02](annotations/D05.json) | [SKILL.md:9-9](inputs/controlled/D05/SKILL.md#L9); [scripts/convert.py:5-10](inputs/controlled/D05/scripts/convert.py#L5) |
| data_flow | D05 | [D05-F05](annotations/D05.json) | [SKILL.md:12-12](inputs/controlled/D05/SKILL.md#L12); [SKILL.md:21-23](inputs/controlled/D05/SKILL.md#L21); [scripts/package.py:7-13](inputs/controlled/D05/scripts/package.py#L7) |
| data_flow | D05 | [D05-F06](annotations/D05.json) | [SKILL.md:8-8](inputs/controlled/D05/SKILL.md#L8); [SKILL.md:13-13](inputs/controlled/D05/SKILL.md#L13) |
| data_flow | D06 | [D06-F01](annotations/D06.json) | [SKILL.md:8-8](inputs/controlled/D06/SKILL.md#L8) |
| data_flow | D06 | [D06-F02](annotations/D06.json) | [SKILL.md:9-9](inputs/controlled/D06/SKILL.md#L9); [scripts/convert.py:5-10](inputs/controlled/D06/scripts/convert.py#L5) |
| data_flow | D06 | [D06-F05](annotations/D06.json) | [SKILL.md:12-12](inputs/controlled/D06/SKILL.md#L12); [SKILL.md:21-23](inputs/controlled/D06/SKILL.md#L21); [scripts/package.py:7-13](inputs/controlled/D06/scripts/package.py#L7) |
| data_flow | D06 | [D06-F06](annotations/D06.json) | [SKILL.md:8-8](inputs/controlled/D06/SKILL.md#L8); [SKILL.md:13-13](inputs/controlled/D06/SKILL.md#L13) |
| data_flow | F01 | [F01-F01](annotations/F01.json) | [SKILL.md:8-8](inputs/controlled/F01/SKILL.md#L8) |
| data_flow | F01 | [F01-F03](annotations/F01.json) | [SKILL.md:8-8](inputs/controlled/F01/SKILL.md#L8); [SKILL.md:9-9](inputs/controlled/F01/SKILL.md#L9) |
| data_flow | F01 | [F01-F07](annotations/F01.json) | [SKILL.md:13-13](inputs/controlled/F01/SKILL.md#L13) |
| data_flow | F02 | [F02-F01](annotations/F02.json) | [SKILL.md:8-8](inputs/controlled/F02/SKILL.md#L8) |
| data_flow | F02 | [F02-F03](annotations/F02.json) | [SKILL.md:8-8](inputs/controlled/F02/SKILL.md#L8) |
| data_flow | F02 | [F02-F07](annotations/F02.json) | [SKILL.md:12-12](inputs/controlled/F02/SKILL.md#L12) |
| data_flow | F03 | [F03-F01](annotations/F03.json) | [SKILL.md:10-10](inputs/controlled/F03/SKILL.md#L10); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| data_flow | F03 | [F03-F03](annotations/F03.json) | [SKILL.md:10-10](inputs/controlled/F03/SKILL.md#L10); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7); [SKILL.md:11-11](inputs/controlled/F03/SKILL.md#L11) |
| data_flow | F03 | [F03-F07](annotations/F03.json) | [SKILL.md:15-15](inputs/controlled/F03/SKILL.md#L15); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| data_flow | F04 | [F04-F01](annotations/F04.json) | [references/workflow.md:3-3](inputs/controlled/F04/references/workflow.md#L3); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| data_flow | F04 | [F04-F03](annotations/F04.json) | [references/workflow.md:3-3](inputs/controlled/F04/references/workflow.md#L3); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8); [references/workflow.md:5-5](inputs/controlled/F04/references/workflow.md#L5) |
| data_flow | F04 | [F04-F07](annotations/F04.json) | [references/workflow.md:15-15](inputs/controlled/F04/references/workflow.md#L15); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| data_flow | F05 | [F05-F01](annotations/F05.json) | [SKILL.md:8-8](inputs/controlled/F05/SKILL.md#L8) |
| data_flow | F05 | [F05-F03](annotations/F05.json) | [SKILL.md:8-8](inputs/controlled/F05/SKILL.md#L8); [SKILL.md:9-9](inputs/controlled/F05/SKILL.md#L9) |
| data_flow | F05 | [F05-F07](annotations/F05.json) | [SKILL.md:13-13](inputs/controlled/F05/SKILL.md#L13) |
| data_flow | F06 | [F06-F01](annotations/F06.json) | [SKILL.md:8-8](inputs/controlled/F06/SKILL.md#L8) |
| data_flow | F06 | [F06-F03](annotations/F06.json) | [SKILL.md:8-8](inputs/controlled/F06/SKILL.md#L8); [SKILL.md:9-9](inputs/controlled/F06/SKILL.md#L9) |
| data_flow | F06 | [F06-F07](annotations/F06.json) | [SKILL.md:13-13](inputs/controlled/F06/SKILL.md#L13) |
| data_flow | N01 | [N01-F04](annotations/N01.json) | [SKILL.md:11-11](inputs/controlled/N01/SKILL.md#L11) |
| data_flow | N01 | [N01-F05](annotations/N01.json) | [SKILL.md:12-12](inputs/controlled/N01/SKILL.md#L12) |
| data_flow | N02 | [N02-F04](annotations/N02.json) | [SKILL.md:10-10](inputs/controlled/N02/SKILL.md#L10) |
| data_flow | N02 | [N02-F05](annotations/N02.json) | [SKILL.md:12-12](inputs/controlled/N02/SKILL.md#L12) |
| data_flow | N03 | [N03-F04](annotations/N03.json) | [SKILL.md:13-13](inputs/controlled/N03/SKILL.md#L13); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| data_flow | N03 | [N03-F05](annotations/N03.json) | [SKILL.md:14-14](inputs/controlled/N03/SKILL.md#L14); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| data_flow | N04 | [N04-F04](annotations/N04.json) | [references/workflow.md:9-9](inputs/controlled/N04/references/workflow.md#L9); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8) |
| data_flow | N04 | [N04-F05](annotations/N04.json) | [references/workflow.md:11-11](inputs/controlled/N04/references/workflow.md#L11); [references/workflow.md:13-13](inputs/controlled/N04/references/workflow.md#L13); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8); [payload.json:1-3](inputs/controlled/N04/payload.json#L1) |
| data_flow | N05 | [N05-F04](annotations/N05.json) | [SKILL.md:11-11](inputs/controlled/N05/SKILL.md#L11) |
| data_flow | N05 | [N05-F05](annotations/N05.json) | [SKILL.md:12-12](inputs/controlled/N05/SKILL.md#L12) |
| data_flow | N06 | [N06-F04](annotations/N06.json) | [SKILL.md:11-11](inputs/controlled/N06/SKILL.md#L11) |
| data_flow | N06 | [N06-F05](annotations/N06.json) | [SKILL.md:12-12](inputs/controlled/N06/SKILL.md#L12) |
| data_flow | Q01 | [Q01-F02](annotations/Q01.json) | [SKILL.md:10-10](inputs/controlled/Q01/SKILL.md#L10) |
| data_flow | Q01 | [Q01-F05](annotations/Q01.json) | [SKILL.md:13-13](inputs/controlled/Q01/SKILL.md#L13) |
| data_flow | Q01 | [Q01-F07](annotations/Q01.json) | [SKILL.md:18-18](inputs/controlled/Q01/SKILL.md#L18) |
| data_flow | Q02 | [Q02-F02](annotations/Q02.json) | [SKILL.md:10-10](inputs/controlled/Q02/SKILL.md#L10) |
| data_flow | Q02 | [Q02-F05](annotations/Q02.json) | [SKILL.md:12-12](inputs/controlled/Q02/SKILL.md#L12) |
| data_flow | Q02 | [Q02-F07](annotations/Q02.json) | [SKILL.md:18-18](inputs/controlled/Q02/SKILL.md#L18) |
| data_flow | Q03 | [Q03-F02](annotations/Q03.json) | [SKILL.md:12-12](inputs/controlled/Q03/SKILL.md#L12) |
| data_flow | Q03 | [Q03-F05](annotations/Q03.json) | [SKILL.md:17-17](inputs/controlled/Q03/SKILL.md#L17); [SKILL.md:13-15](inputs/controlled/Q03/SKILL.md#L13) |
| data_flow | Q03 | [Q03-F07](annotations/Q03.json) | [SKILL.md:25-25](inputs/controlled/Q03/SKILL.md#L25) |
| data_flow | Q04 | [Q04-F02](annotations/Q04.json) | [references/workflow.md:7-7](inputs/controlled/Q04/references/workflow.md#L7); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8) |
| data_flow | Q04 | [Q04-F05](annotations/Q04.json) | [references/workflow.md:12-12](inputs/controlled/Q04/references/workflow.md#L12); [references/workflow.md:9-9](inputs/controlled/Q04/references/workflow.md#L9); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8) |
| data_flow | Q04 | [Q04-F07](annotations/Q04.json) | [references/workflow.md:23-23](inputs/controlled/Q04/references/workflow.md#L23); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8) |
| data_flow | Q05 | [Q05-F02](annotations/Q05.json) | [SKILL.md:10-10](inputs/controlled/Q05/SKILL.md#L10) |
| data_flow | Q05 | [Q05-F05](annotations/Q05.json) | [SKILL.md:13-13](inputs/controlled/Q05/SKILL.md#L13) |
| data_flow | Q05 | [Q05-F07](annotations/Q05.json) | [SKILL.md:18-18](inputs/controlled/Q05/SKILL.md#L18) |
| data_flow | Q06 | [Q06-F02](annotations/Q06.json) | [SKILL.md:10-10](inputs/controlled/Q06/SKILL.md#L10) |
| data_flow | Q06 | [Q06-F05](annotations/Q06.json) | [SKILL.md:13-13](inputs/controlled/Q06/SKILL.md#L13) |
| data_flow | Q06 | [Q06-F07](annotations/Q06.json) | [SKILL.md:18-18](inputs/controlled/Q06/SKILL.md#L18) |
| data_flow | R02 | [R02-F06](annotations/R02.json) | [SKILL.md:124-130](inputs/upstream/playwright/SKILL.md#L124); [scripts/playwright_cli.sh:9-25](inputs/upstream/playwright/scripts/playwright_cli.sh#L9) |
| data_flow | R06 | [R06-F06](annotations/R06.json) | [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:155-186](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L155) |
| data_flow | R06 | [R06-F11](annotations/R06.json) | [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:169-186](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L169); [scripts/transcribe_diarize.py:252-264](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L252) |
| data_source | R01 | [R01-F04](annotations/R01.json) | [SKILL.md:15-17](inputs/upstream/pdf/SKILL.md#L15); [SKILL.md:52-55](inputs/upstream/pdf/SKILL.md#L52) |
| data_source | R02 | [R02-F03](annotations/R02.json) | [SKILL.md:63-69](inputs/upstream/playwright/SKILL.md#L63) |
| data_source | R03 | [R03-F02](annotations/R03.json) | [SKILL.md:16-20](inputs/upstream/gh-fix-ci/SKILL.md#L16); [SKILL.md:32-38](inputs/upstream/gh-fix-ci/SKILL.md#L32) |
| data_source | R03 | [R03-F05](annotations/R03.json) | [SKILL.md:42-46](inputs/upstream/gh-fix-ci/SKILL.md#L42); [scripts/inspect_pr_checks.py:333-355](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L333); [scripts/inspect_pr_checks.py:366-377](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L366) |
| data_source | R04 | [R04-F02](annotations/R04.json) | [SKILL.md:70-98](inputs/upstream/netlify-deploy/SKILL.md#L70) |
| data_source | R04 | [R04-F05](annotations/R04.json) | [SKILL.md:106-116](inputs/upstream/netlify-deploy/SKILL.md#L106); [SKILL.md:138-150](inputs/upstream/netlify-deploy/SKILL.md#L138) |
| data_source | R05 | [R05-F04](annotations/R05.json) | [SKILL.md:40-50](inputs/upstream/linear/SKILL.md#L40) |
| data_source | R06 | [R06-F01](annotations/R06.json) | [SKILL.md:11-16](inputs/upstream/transcribe/SKILL.md#L11) |
| data_source | R06 | [R06-F05](annotations/R06.json) | [SKILL.md:61-70](inputs/upstream/transcribe/SKILL.md#L61); [SKILL.md:80-81](inputs/upstream/transcribe/SKILL.md#L80); [references/api.md:7-7](inputs/upstream/transcribe/references/api.md#L7); [scripts/transcribe_diarize.py:74-98](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L74); [scripts/transcribe_diarize.py:169-174](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L169) |
| data_source | R06 | [R06-F10](annotations/R06.json) | [SKILL.md:12-12](inputs/upstream/transcribe/SKILL.md#L12); [SKILL.md:53-78](inputs/upstream/transcribe/SKILL.md#L53) |
| example_vs_instruction | R02 | [R02-F09](annotations/R02.json) | [SKILL.md:132-137](inputs/upstream/playwright/SKILL.md#L132); [references/workflows.md:72-89](inputs/upstream/playwright/references/workflows.md#L72) |
| example_vs_instruction | R04 | [R04-F04](annotations/R04.json) | [SKILL.md:118-136](inputs/upstream/netlify-deploy/SKILL.md#L118); [SKILL.md:243-247](inputs/upstream/netlify-deploy/SKILL.md#L243); [references/deployment-patterns.md:70-90](inputs/upstream/netlify-deploy/references/deployment-patterns.md#L70) |
| example_vs_instruction | R06 | [R06-F10](annotations/R06.json) | [SKILL.md:12-12](inputs/upstream/transcribe/SKILL.md#L12); [SKILL.md:53-78](inputs/upstream/transcribe/SKILL.md#L53) |
| exception | N01 | [N01-F03](annotations/N01.json) | [SKILL.md:9-9](inputs/controlled/N01/SKILL.md#L9); [SKILL.md:10-10](inputs/controlled/N01/SKILL.md#L10) |
| exception | N02 | [N02-F03](annotations/N02.json) | [SKILL.md:8-8](inputs/controlled/N02/SKILL.md#L8); [SKILL.md:10-10](inputs/controlled/N02/SKILL.md#L10) |
| exception | N03 | [N03-F03](annotations/N03.json) | [SKILL.md:11-11](inputs/controlled/N03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7); [SKILL.md:12-12](inputs/controlled/N03/SKILL.md#L12) |
| exception | N04 | [N04-F03](annotations/N04.json) | [references/workflow.md:6-6](inputs/controlled/N04/references/workflow.md#L6); [references/workflow.md:5-5](inputs/controlled/N04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8); [references/workflow.md:7-7](inputs/controlled/N04/references/workflow.md#L7) |
| exception | N05 | [N05-F03](annotations/N05.json) | [SKILL.md:9-9](inputs/controlled/N05/SKILL.md#L9); [SKILL.md:10-10](inputs/controlled/N05/SKILL.md#L10) |
| exception | N06 | [N06-F03](annotations/N06.json) | [SKILL.md:9-9](inputs/controlled/N06/SKILL.md#L9); [SKILL.md:10-10](inputs/controlled/N06/SKILL.md#L10) |
| exception_condition | R02 | [R02-F01](annotations/R02.json) | [SKILL.md:9-10](inputs/upstream/playwright/SKILL.md#L9); [SKILL.md:122-130](inputs/upstream/playwright/SKILL.md#L122); [SKILL.md:57-62](inputs/upstream/playwright/SKILL.md#L57) |
| exception_condition | R02 | [R02-F05](annotations/R02.json) | [SKILL.md:139-147](inputs/upstream/playwright/SKILL.md#L139) |
| exception_condition | R04 | [R04-F04](annotations/R04.json) | [SKILL.md:118-136](inputs/upstream/netlify-deploy/SKILL.md#L118); [SKILL.md:243-247](inputs/upstream/netlify-deploy/SKILL.md#L243); [references/deployment-patterns.md:70-90](inputs/upstream/netlify-deploy/references/deployment-patterns.md#L70) |
| external_input_boundary | R04 | [R04-F10](annotations/R04.json) | [SKILL.md:238-247](inputs/upstream/netlify-deploy/SKILL.md#L238) |
| fallback | F01 | [F01-F05](annotations/F01.json) | [SKILL.md:11-11](inputs/controlled/F01/SKILL.md#L11) |
| fallback | F02 | [F02-F05](annotations/F02.json) | [SKILL.md:10-10](inputs/controlled/F02/SKILL.md#L10) |
| fallback | F03 | [F03-F05](annotations/F03.json) | [SKILL.md:13-13](inputs/controlled/F03/SKILL.md#L13); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| fallback | F04 | [F04-F05](annotations/F04.json) | [references/workflow.md:9-9](inputs/controlled/F04/references/workflow.md#L9); [references/workflow.md:7-7](inputs/controlled/F04/references/workflow.md#L7); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| fallback | F05 | [F05-F05](annotations/F05.json) | [SKILL.md:11-11](inputs/controlled/F05/SKILL.md#L11) |
| fallback | F06 | [F06-F05](annotations/F06.json) | [SKILL.md:11-11](inputs/controlled/F06/SKILL.md#L11) |
| fallback_path | R01 | [R01-F02](annotations/R01.json) | [SKILL.md:14-20](inputs/upstream/pdf/SKILL.md#L14); [SKILL.md:47-47](inputs/upstream/pdf/SKILL.md#L47) |
| fallback_path | R02 | [R02-F04](annotations/R02.json) | [SKILL.md:80-89](inputs/upstream/playwright/SKILL.md#L80); [SKILL.md:132-137](inputs/upstream/playwright/SKILL.md#L132); [references/workflows.md:91-95](inputs/upstream/playwright/references/workflows.md#L91) |
| fallback_path | R03 | [R03-F04](annotations/R03.json) | [SKILL.md:39-44](inputs/upstream/gh-fix-ci/SKILL.md#L39); [scripts/inspect_pr_checks.py:182-215](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L182) |
| fallback_path | R03 | [R03-F05](annotations/R03.json) | [SKILL.md:42-46](inputs/upstream/gh-fix-ci/SKILL.md#L42); [scripts/inspect_pr_checks.py:333-355](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L333); [scripts/inspect_pr_checks.py:366-377](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L366) |
| fallback_path | R04 | [R04-F01](annotations/R04.json) | [SKILL.md:30-36](inputs/upstream/netlify-deploy/SKILL.md#L30); [SKILL.md:52-66](inputs/upstream/netlify-deploy/SKILL.md#L52) |
| fallback_path | R04 | [R04-F07](annotations/R04.json) | [SKILL.md:192-209](inputs/upstream/netlify-deploy/SKILL.md#L192) |
| fallback_path | R05 | [R05-F02](annotations/R05.json) | [SKILL.md:22-33](inputs/upstream/linear/SKILL.md#L22) |
| fallback_path | R05 | [R05-F10](annotations/R05.json) | [SKILL.md:82-87](inputs/upstream/linear/SKILL.md#L82) |
| global_constraint | R01 | [R01-F06](annotations/R01.json) | [SKILL.md:22-25](inputs/upstream/pdf/SKILL.md#L22) |
| global_constraint | R01 | [R01-F08](annotations/R01.json) | [SKILL.md:57-62](inputs/upstream/pdf/SKILL.md#L57); [SKILL.md:64-67](inputs/upstream/pdf/SKILL.md#L64) |
| global_constraint | R04 | [R04-F09](annotations/R04.json) | [SKILL.md:223-229](inputs/upstream/netlify-deploy/SKILL.md#L223); [SKILL.md:243-247](inputs/upstream/netlify-deploy/SKILL.md#L243); [references/cli-commands.md:82-96](inputs/upstream/netlify-deploy/references/cli-commands.md#L82) |
| global_constraint | R05 | [R05-F01](annotations/R05.json) | [SKILL.md:14-20](inputs/upstream/linear/SKILL.md#L14) |
| global_constraint | R06 | [R06-F02](annotations/R06.json) | [SKILL.md:13-14](inputs/upstream/transcribe/SKILL.md#L13); [SKILL.md:39-42](inputs/upstream/transcribe/SKILL.md#L39) |
| instruction_vs_suggestion | R03 | [R03-F08](annotations/R03.json) | [SKILL.md:55-58](inputs/upstream/gh-fix-ci/SKILL.md#L55) |
| json | N04 | [N04-F05](annotations/N04.json) | [references/workflow.md:11-11](inputs/controlled/N04/references/workflow.md#L11); [references/workflow.md:13-13](inputs/controlled/N04/references/workflow.md#L13); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8); [payload.json:1-3](inputs/controlled/N04/payload.json#L1) |
| local_constraint | R01 | [R01-F03](annotations/R01.json) | [SKILL.md:19-20](inputs/upstream/pdf/SKILL.md#L19) |
| local_constraint | R02 | [R02-F05](annotations/R02.json) | [SKILL.md:139-147](inputs/upstream/playwright/SKILL.md#L139) |
| local_constraint | R02 | [R02-F08](annotations/R02.json) | [SKILL.md:146-146](inputs/upstream/playwright/SKILL.md#L146); [SKILL.md:132-137](inputs/upstream/playwright/SKILL.md#L132); [references/workflows.md:3-5](inputs/upstream/playwright/references/workflows.md#L3) |
| local_constraint | R03 | [R03-F06](annotations/R03.json) | [SKILL.md:47-49](inputs/upstream/gh-fix-ci/SKILL.md#L47); [scripts/inspect_pr_checks.py:244-257](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L244) |
| local_constraint | R04 | [R04-F08](annotations/R04.json) | [SKILL.md:213-220](inputs/upstream/netlify-deploy/SKILL.md#L213) |
| local_constraint | R05 | [R05-F05](annotations/R05.json) | [SKILL.md:46-50](inputs/upstream/linear/SKILL.md#L46) |
| local_constraint | R05 | [R05-F08](annotations/R05.json) | [SKILL.md:52-53](inputs/upstream/linear/SKILL.md#L52); [SKILL.md:75-80](inputs/upstream/linear/SKILL.md#L75) |
| local_constraint | R05 | [R05-F10](annotations/R05.json) | [SKILL.md:82-87](inputs/upstream/linear/SKILL.md#L82) |
| local_constraint | R06 | [R06-F04](annotations/R06.json) | [SKILL.md:22-22](inputs/upstream/transcribe/SKILL.md#L22); [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:241-244](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L241) |
| local_constraint | R06 | [R06-F08](annotations/R06.json) | [SKILL.md:24-26](inputs/upstream/transcribe/SKILL.md#L24); [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:234-239](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L234); [scripts/transcribe_diarize.py:101-123](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L101); [scripts/transcribe_diarize.py:263-272](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L263) |
| local_constraint | R06 | [R06-F11](annotations/R06.json) | [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:169-186](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L169); [scripts/transcribe_diarize.py:252-264](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L252) |
| metadata_vs_execution | R05 | [R05-F09](annotations/R05.json) | [SKILL.md:14-16](inputs/upstream/linear/SKILL.md#L14); [agents/openai.yaml:1-14](inputs/upstream/linear/agents/openai.yaml#L1) |
| must_not_infer | R01 | [R01-F03](annotations/R01.json) | [SKILL.md:19-20](inputs/upstream/pdf/SKILL.md#L19) |
| must_not_infer | R01 | [R01-F07](annotations/R01.json) | [SKILL.md:27-45](inputs/upstream/pdf/SKILL.md#L27) |
| must_not_infer | R01 | [R01-F08](annotations/R01.json) | [SKILL.md:57-62](inputs/upstream/pdf/SKILL.md#L57); [SKILL.md:64-67](inputs/upstream/pdf/SKILL.md#L64) |
| must_not_infer | R02 | [R02-F07](annotations/R02.json) | [SKILL.md:132-137](inputs/upstream/playwright/SKILL.md#L132); [references/cli.md:19-49](inputs/upstream/playwright/references/cli.md#L19) |
| must_not_infer | R02 | [R02-F09](annotations/R02.json) | [SKILL.md:132-137](inputs/upstream/playwright/SKILL.md#L132); [references/workflows.md:72-89](inputs/upstream/playwright/references/workflows.md#L72) |
| must_not_infer | R03 | [R03-F06](annotations/R03.json) | [SKILL.md:47-49](inputs/upstream/gh-fix-ci/SKILL.md#L47); [scripts/inspect_pr_checks.py:244-257](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L244) |
| must_not_infer | R03 | [R03-F08](annotations/R03.json) | [SKILL.md:55-58](inputs/upstream/gh-fix-ci/SKILL.md#L55) |
| must_not_infer | R03 | [R03-F09](annotations/R03.json) | [SKILL.md:64-64](inputs/upstream/gh-fix-ci/SKILL.md#L64); [scripts/inspect_pr_checks.py:110-135](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L110) |
| must_not_infer | R04 | [R04-F04](annotations/R04.json) | [SKILL.md:118-136](inputs/upstream/netlify-deploy/SKILL.md#L118); [SKILL.md:243-247](inputs/upstream/netlify-deploy/SKILL.md#L243); [references/deployment-patterns.md:70-90](inputs/upstream/netlify-deploy/references/deployment-patterns.md#L70) |
| must_not_infer | R04 | [R04-F06](annotations/R04.json) | [SKILL.md:152-163](inputs/upstream/netlify-deploy/SKILL.md#L152); [SKILL.md:243-247](inputs/upstream/netlify-deploy/SKILL.md#L243); [references/netlify-toml.md:13-33](inputs/upstream/netlify-deploy/references/netlify-toml.md#L13) |
| must_not_infer | R04 | [R04-F09](annotations/R04.json) | [SKILL.md:223-229](inputs/upstream/netlify-deploy/SKILL.md#L223); [SKILL.md:243-247](inputs/upstream/netlify-deploy/SKILL.md#L243); [references/cli-commands.md:82-96](inputs/upstream/netlify-deploy/references/cli-commands.md#L82) |
| must_not_infer | R04 | [R04-F10](annotations/R04.json) | [SKILL.md:238-247](inputs/upstream/netlify-deploy/SKILL.md#L238) |
| must_not_infer | R05 | [R05-F03](annotations/R05.json) | [SKILL.md:35-38](inputs/upstream/linear/SKILL.md#L35) |
| must_not_infer | R05 | [R05-F05](annotations/R05.json) | [SKILL.md:46-50](inputs/upstream/linear/SKILL.md#L46) |
| must_not_infer | R05 | [R05-F06](annotations/R05.json) | [SKILL.md:43-44](inputs/upstream/linear/SKILL.md#L43); [SKILL.md:55-61](inputs/upstream/linear/SKILL.md#L55) |
| must_not_infer | R05 | [R05-F09](annotations/R05.json) | [SKILL.md:14-16](inputs/upstream/linear/SKILL.md#L14); [agents/openai.yaml:1-14](inputs/upstream/linear/agents/openai.yaml#L1) |
| must_not_infer | R05 | [R05-F10](annotations/R05.json) | [SKILL.md:82-87](inputs/upstream/linear/SKILL.md#L82) |
| must_not_infer | R06 | [R06-F07](annotations/R06.json) | [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:33-40](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L33); [scripts/transcribe_diarize.py:246-264](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L246) |
| must_not_infer | R06 | [R06-F08](annotations/R06.json) | [SKILL.md:24-26](inputs/upstream/transcribe/SKILL.md#L24); [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:234-239](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L234); [scripts/transcribe_diarize.py:101-123](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L101); [scripts/transcribe_diarize.py:263-272](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L263) |
| must_not_infer | R06 | [R06-F09](annotations/R06.json) | [SKILL.md:80-81](inputs/upstream/transcribe/SKILL.md#L80); [references/api.md:3-6](inputs/upstream/transcribe/references/api.md#L3); [scripts/transcribe_diarize.py:18-19](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L18); [scripts/transcribe_diarize.py:145-152](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L145) |
| must_not_infer | R06 | [R06-F10](annotations/R06.json) | [SKILL.md:12-12](inputs/upstream/transcribe/SKILL.md#L12); [SKILL.md:53-78](inputs/upstream/transcribe/SKILL.md#L53) |
| must_not_infer | R06 | [R06-F11](annotations/R06.json) | [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:169-186](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L169); [scripts/transcribe_diarize.py:252-264](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L252) |
| negation | D01 | [D01-F04](annotations/D01.json) | [SKILL.md:9-9](inputs/controlled/D01/SKILL.md#L9); [SKILL.md:11-11](inputs/controlled/D01/SKILL.md#L11); [scripts/convert.py:5-10](inputs/controlled/D01/scripts/convert.py#L5) |
| negation | D02 | [D02-F04](annotations/D02.json) | [SKILL.md:8-8](inputs/controlled/D02/SKILL.md#L8); [SKILL.md:10-10](inputs/controlled/D02/SKILL.md#L10); [scripts/convert.py:5-10](inputs/controlled/D02/scripts/convert.py#L5) |
| negation | D03 | [D03-F04](annotations/D03.json) | [SKILL.md:11-11](inputs/controlled/D03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [SKILL.md:13-13](inputs/controlled/D03/SKILL.md#L13); [scripts/convert.py:5-10](inputs/controlled/D03/scripts/convert.py#L5) |
| negation | D04 | [D04-F04](annotations/D04.json) | [references/workflow.md:6-6](inputs/controlled/D04/references/workflow.md#L6); [references/workflow.md:5-5](inputs/controlled/D04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8); [references/workflow.md:9-9](inputs/controlled/D04/references/workflow.md#L9); [scripts/convert.py:5-10](inputs/controlled/D04/scripts/convert.py#L5) |
| negation | D05 | [D05-F04](annotations/D05.json) | [SKILL.md:9-9](inputs/controlled/D05/SKILL.md#L9); [SKILL.md:11-11](inputs/controlled/D05/SKILL.md#L11); [scripts/convert.py:5-10](inputs/controlled/D05/scripts/convert.py#L5) |
| negation | D05 | [D05-F07](annotations/D05.json) | [SKILL.md:14-14](inputs/controlled/D05/SKILL.md#L14) |
| negation | D06 | [D06-F04](annotations/D06.json) | [SKILL.md:9-9](inputs/controlled/D06/SKILL.md#L9); [SKILL.md:11-11](inputs/controlled/D06/SKILL.md#L11); [scripts/convert.py:5-10](inputs/controlled/D06/scripts/convert.py#L5) |
| negation | F01 | [F01-F04](annotations/F01.json) | [SKILL.md:10-10](inputs/controlled/F01/SKILL.md#L10) |
| negation | F01 | [F01-F08](annotations/F01.json) | [SKILL.md:14-14](inputs/controlled/F01/SKILL.md#L14) |
| negation | F02 | [F02-F04](annotations/F02.json) | [SKILL.md:10-10](inputs/controlled/F02/SKILL.md#L10) |
| negation | F02 | [F02-F08](annotations/F02.json) | [SKILL.md:14-14](inputs/controlled/F02/SKILL.md#L14) |
| negation | F03 | [F03-F04](annotations/F03.json) | [SKILL.md:12-12](inputs/controlled/F03/SKILL.md#L12); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| negation | F03 | [F03-F08](annotations/F03.json) | [SKILL.md:16-16](inputs/controlled/F03/SKILL.md#L16); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| negation | F04 | [F04-F04](annotations/F04.json) | [references/workflow.md:8-8](inputs/controlled/F04/references/workflow.md#L8); [references/workflow.md:7-7](inputs/controlled/F04/references/workflow.md#L7); [references/workflow.md:11-11](inputs/controlled/F04/references/workflow.md#L11); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8); [retry.yaml:1-3](inputs/controlled/F04/retry.yaml#L1) |
| negation | F04 | [F04-F08](annotations/F04.json) | [references/workflow.md:17-17](inputs/controlled/F04/references/workflow.md#L17); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| negation | F05 | [F05-F04](annotations/F05.json) | [SKILL.md:10-10](inputs/controlled/F05/SKILL.md#L10) |
| negation | F05 | [F05-F08](annotations/F05.json) | [SKILL.md:14-14](inputs/controlled/F05/SKILL.md#L14) |
| negation | F05 | [F05-F10](annotations/F05.json) | [SKILL.md:16-16](inputs/controlled/F05/SKILL.md#L16) |
| negation | F06 | [F06-F04](annotations/F06.json) | [SKILL.md:10-10](inputs/controlled/F06/SKILL.md#L10) |
| negation | F06 | [F06-F08](annotations/F06.json) | [SKILL.md:14-14](inputs/controlled/F06/SKILL.md#L14) |
| negation | N01 | [N01-F02](annotations/N01.json) | [SKILL.md:9-9](inputs/controlled/N01/SKILL.md#L9); [SKILL.md:10-10](inputs/controlled/N01/SKILL.md#L10) |
| negation | N01 | [N01-F06](annotations/N01.json) | [SKILL.md:13-13](inputs/controlled/N01/SKILL.md#L13) |
| negation | N01 | [N01-F08](annotations/N01.json) | [SKILL.md:15-15](inputs/controlled/N01/SKILL.md#L15) |
| negation | N02 | [N02-F02](annotations/N02.json) | [SKILL.md:8-8](inputs/controlled/N02/SKILL.md#L8); [SKILL.md:10-10](inputs/controlled/N02/SKILL.md#L10) |
| negation | N02 | [N02-F06](annotations/N02.json) | [SKILL.md:12-12](inputs/controlled/N02/SKILL.md#L12) |
| negation | N02 | [N02-F08](annotations/N02.json) | [SKILL.md:14-14](inputs/controlled/N02/SKILL.md#L14) |
| negation | N03 | [N03-F02](annotations/N03.json) | [SKILL.md:11-11](inputs/controlled/N03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7); [SKILL.md:12-12](inputs/controlled/N03/SKILL.md#L12) |
| negation | N03 | [N03-F06](annotations/N03.json) | [SKILL.md:15-15](inputs/controlled/N03/SKILL.md#L15); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| negation | N03 | [N03-F08](annotations/N03.json) | [SKILL.md:17-17](inputs/controlled/N03/SKILL.md#L17); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| negation | N04 | [N04-F02](annotations/N04.json) | [references/workflow.md:6-6](inputs/controlled/N04/references/workflow.md#L6); [references/workflow.md:5-5](inputs/controlled/N04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8); [references/workflow.md:7-7](inputs/controlled/N04/references/workflow.md#L7) |
| negation | N04 | [N04-F06](annotations/N04.json) | [references/workflow.md:15-15](inputs/controlled/N04/references/workflow.md#L15); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8) |
| negation | N04 | [N04-F08](annotations/N04.json) | [references/workflow.md:19-19](inputs/controlled/N04/references/workflow.md#L19); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8) |
| negation | N05 | [N05-F02](annotations/N05.json) | [SKILL.md:9-9](inputs/controlled/N05/SKILL.md#L9); [SKILL.md:10-10](inputs/controlled/N05/SKILL.md#L10) |
| negation | N05 | [N05-F06](annotations/N05.json) | [SKILL.md:13-13](inputs/controlled/N05/SKILL.md#L13) |
| negation | N05 | [N05-F08](annotations/N05.json) | [SKILL.md:15-15](inputs/controlled/N05/SKILL.md#L15) |
| negation | N05 | [N05-F09](annotations/N05.json) | [SKILL.md:16-16](inputs/controlled/N05/SKILL.md#L16) |
| negation | N06 | [N06-F02](annotations/N06.json) | [SKILL.md:9-9](inputs/controlled/N06/SKILL.md#L9); [SKILL.md:10-10](inputs/controlled/N06/SKILL.md#L10) |
| negation | N06 | [N06-F06](annotations/N06.json) | [SKILL.md:13-13](inputs/controlled/N06/SKILL.md#L13) |
| negation | N06 | [N06-F08](annotations/N06.json) | [SKILL.md:15-15](inputs/controlled/N06/SKILL.md#L15) |
| negation | Q01 | [Q01-F09](annotations/Q01.json) | [SKILL.md:8-8](inputs/controlled/Q01/SKILL.md#L8) |
| negation | Q01 | [Q01-F10](annotations/Q01.json) | [SKILL.md:11-11](inputs/controlled/Q01/SKILL.md#L11); [SKILL.md:16-16](inputs/controlled/Q01/SKILL.md#L16) |
| negation | Q02 | [Q02-F09](annotations/Q02.json) | [SKILL.md:8-8](inputs/controlled/Q02/SKILL.md#L8) |
| negation | Q02 | [Q02-F10](annotations/Q02.json) | [SKILL.md:10-10](inputs/controlled/Q02/SKILL.md#L10); [SKILL.md:16-16](inputs/controlled/Q02/SKILL.md#L16) |
| negation | Q03 | [Q03-F09](annotations/Q03.json) | [SKILL.md:8-8](inputs/controlled/Q03/SKILL.md#L8) |
| negation | Q03 | [Q03-F10](annotations/Q03.json) | [SKILL.md:16-16](inputs/controlled/Q03/SKILL.md#L16); [SKILL.md:13-15](inputs/controlled/Q03/SKILL.md#L13); [SKILL.md:21-21](inputs/controlled/Q03/SKILL.md#L21) |
| negation | Q04 | [Q04-F09](annotations/Q04.json) | [references/workflow.md:3-3](inputs/controlled/Q04/references/workflow.md#L3); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8) |
| negation | Q04 | [Q04-F10](annotations/Q04.json) | [references/workflow.md:10-10](inputs/controlled/Q04/references/workflow.md#L10); [references/workflow.md:9-9](inputs/controlled/Q04/references/workflow.md#L9); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8); [references/workflow.md:19-19](inputs/controlled/Q04/references/workflow.md#L19) |
| negation | Q05 | [Q05-F09](annotations/Q05.json) | [SKILL.md:8-8](inputs/controlled/Q05/SKILL.md#L8) |
| negation | Q05 | [Q05-F10](annotations/Q05.json) | [SKILL.md:11-11](inputs/controlled/Q05/SKILL.md#L11); [SKILL.md:16-16](inputs/controlled/Q05/SKILL.md#L16) |
| negation | Q05 | [Q05-F11](annotations/Q05.json) | [SKILL.md:17-17](inputs/controlled/Q05/SKILL.md#L17) |
| negation | Q06 | [Q06-F09](annotations/Q06.json) | [SKILL.md:8-8](inputs/controlled/Q06/SKILL.md#L8) |
| negation | Q06 | [Q06-F10](annotations/Q06.json) | [SKILL.md:11-11](inputs/controlled/Q06/SKILL.md#L11); [SKILL.md:16-16](inputs/controlled/Q06/SKILL.md#L16) |
| nested_list | D04 | [D04-F02](annotations/D04.json) | [references/workflow.md:6-6](inputs/controlled/D04/references/workflow.md#L6); [references/workflow.md:5-5](inputs/controlled/D04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8); [scripts/convert.py:5-10](inputs/controlled/D04/scripts/convert.py#L5) |
| nested_list | D04 | [D04-F03](annotations/D04.json) | [references/workflow.md:7-7](inputs/controlled/D04/references/workflow.md#L7); [references/workflow.md:5-5](inputs/controlled/D04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8) |
| nested_list | D04 | [D04-F04](annotations/D04.json) | [references/workflow.md:6-6](inputs/controlled/D04/references/workflow.md#L6); [references/workflow.md:5-5](inputs/controlled/D04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8); [references/workflow.md:9-9](inputs/controlled/D04/references/workflow.md#L9); [scripts/convert.py:5-10](inputs/controlled/D04/scripts/convert.py#L5) |
| nested_list | F04 | [F04-F04](annotations/F04.json) | [references/workflow.md:8-8](inputs/controlled/F04/references/workflow.md#L8); [references/workflow.md:7-7](inputs/controlled/F04/references/workflow.md#L7); [references/workflow.md:11-11](inputs/controlled/F04/references/workflow.md#L11); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8); [retry.yaml:1-3](inputs/controlled/F04/retry.yaml#L1) |
| nested_list | F04 | [F04-F05](annotations/F04.json) | [references/workflow.md:9-9](inputs/controlled/F04/references/workflow.md#L9); [references/workflow.md:7-7](inputs/controlled/F04/references/workflow.md#L7); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| nested_list | N04 | [N04-F02](annotations/N04.json) | [references/workflow.md:6-6](inputs/controlled/N04/references/workflow.md#L6); [references/workflow.md:5-5](inputs/controlled/N04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8); [references/workflow.md:7-7](inputs/controlled/N04/references/workflow.md#L7) |
| nested_list | N04 | [N04-F03](annotations/N04.json) | [references/workflow.md:6-6](inputs/controlled/N04/references/workflow.md#L6); [references/workflow.md:5-5](inputs/controlled/N04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8); [references/workflow.md:7-7](inputs/controlled/N04/references/workflow.md#L7) |
| nested_list | Q04 | [Q04-F03](annotations/Q04.json) | [references/workflow.md:10-10](inputs/controlled/Q04/references/workflow.md#L10); [references/workflow.md:9-9](inputs/controlled/Q04/references/workflow.md#L9); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8) |
| nested_list | Q04 | [Q04-F04](annotations/Q04.json) | [references/workflow.md:11-11](inputs/controlled/Q04/references/workflow.md#L11); [references/workflow.md:9-9](inputs/controlled/Q04/references/workflow.md#L9); [references/workflow.md:15-15](inputs/controlled/Q04/references/workflow.md#L15); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8); [query.yaml:2-2](inputs/controlled/Q04/query.yaml#L2); [query.yaml:1-1](inputs/controlled/Q04/query.yaml#L1) |
| nested_list | Q04 | [Q04-F05](annotations/Q04.json) | [references/workflow.md:12-12](inputs/controlled/Q04/references/workflow.md#L12); [references/workflow.md:9-9](inputs/controlled/Q04/references/workflow.md#L9); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8) |
| nested_list | Q04 | [Q04-F06](annotations/Q04.json) | [references/workflow.md:13-13](inputs/controlled/Q04/references/workflow.md#L13); [references/workflow.md:9-9](inputs/controlled/Q04/references/workflow.md#L9); [references/workflow.md:15-15](inputs/controlled/Q04/references/workflow.md#L15); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8); [query.yaml:3-3](inputs/controlled/Q04/query.yaml#L3); [query.yaml:1-1](inputs/controlled/Q04/query.yaml#L1) |
| nested_list | Q04 | [Q04-F10](annotations/Q04.json) | [references/workflow.md:10-10](inputs/controlled/Q04/references/workflow.md#L10); [references/workflow.md:9-9](inputs/controlled/Q04/references/workflow.md#L9); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8); [references/workflow.md:19-19](inputs/controlled/Q04/references/workflow.md#L19) |
| nested_list | R01 | [R01-F02](annotations/R01.json) | [SKILL.md:14-20](inputs/upstream/pdf/SKILL.md#L14); [SKILL.md:47-47](inputs/upstream/pdf/SKILL.md#L47) |
| output_delivery | R01 | [R01-F06](annotations/R01.json) | [SKILL.md:22-25](inputs/upstream/pdf/SKILL.md#L22) |
| output_delivery | R01 | [R01-F08](annotations/R01.json) | [SKILL.md:57-62](inputs/upstream/pdf/SKILL.md#L57); [SKILL.md:64-67](inputs/upstream/pdf/SKILL.md#L64) |
| output_delivery | R02 | [R02-F08](annotations/R02.json) | [SKILL.md:146-146](inputs/upstream/playwright/SKILL.md#L146); [SKILL.md:132-137](inputs/upstream/playwright/SKILL.md#L132); [references/workflows.md:3-5](inputs/upstream/playwright/references/workflows.md#L3) |
| output_delivery | R03 | [R03-F03](annotations/R03.json) | [SKILL.md:35-38](inputs/upstream/gh-fix-ci/SKILL.md#L35); [SKILL.md:60-69](inputs/upstream/gh-fix-ci/SKILL.md#L60) |
| output_delivery | R03 | [R03-F07](annotations/R03.json) | [SKILL.md:50-58](inputs/upstream/gh-fix-ci/SKILL.md#L50) |
| output_delivery | R03 | [R03-F09](annotations/R03.json) | [SKILL.md:64-64](inputs/upstream/gh-fix-ci/SKILL.md#L64); [scripts/inspect_pr_checks.py:110-135](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L110) |
| output_delivery | R04 | [R04-F05](annotations/R04.json) | [SKILL.md:106-116](inputs/upstream/netlify-deploy/SKILL.md#L106); [SKILL.md:138-150](inputs/upstream/netlify-deploy/SKILL.md#L138) |
| output_delivery | R05 | [R05-F08](annotations/R05.json) | [SKILL.md:52-53](inputs/upstream/linear/SKILL.md#L52); [SKILL.md:75-80](inputs/upstream/linear/SKILL.md#L75) |
| output_delivery | R06 | [R06-F01](annotations/R06.json) | [SKILL.md:11-16](inputs/upstream/transcribe/SKILL.md#L11) |
| output_delivery | R06 | [R06-F08](annotations/R06.json) | [SKILL.md:24-26](inputs/upstream/transcribe/SKILL.md#L24); [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:234-239](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L234); [scripts/transcribe_diarize.py:101-123](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L101); [scripts/transcribe_diarize.py:263-272](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L263) |
| parameter_default | Q06 | [Q06-F06](annotations/Q06.json) | [SKILL.md:14-14](inputs/controlled/Q06/SKILL.md#L14) |
| parameter_defaults | R06 | [R06-F03](annotations/R06.json) | [SKILL.md:18-22](inputs/upstream/transcribe/SKILL.md#L18) |
| parameter_defaults | R06 | [R06-F08](annotations/R06.json) | [SKILL.md:24-26](inputs/upstream/transcribe/SKILL.md#L24); [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:234-239](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L234); [scripts/transcribe_diarize.py:101-123](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L101); [scripts/transcribe_diarize.py:263-272](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L263) |
| parameter_format | R06 | [R06-F05](annotations/R06.json) | [SKILL.md:61-70](inputs/upstream/transcribe/SKILL.md#L61); [SKILL.md:80-81](inputs/upstream/transcribe/SKILL.md#L80); [references/api.md:7-7](inputs/upstream/transcribe/references/api.md#L7); [scripts/transcribe_diarize.py:74-98](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L74); [scripts/transcribe_diarize.py:169-174](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L169) |
| parameter_omission | Q01 | [Q01-F04](annotations/Q01.json) | [SKILL.md:12-12](inputs/controlled/Q01/SKILL.md#L12) |
| parameter_omission | Q01 | [Q01-F06](annotations/Q01.json) | [SKILL.md:14-14](inputs/controlled/Q01/SKILL.md#L14) |
| parameter_omission | Q02 | [Q02-F04](annotations/Q02.json) | [SKILL.md:12-12](inputs/controlled/Q02/SKILL.md#L12) |
| parameter_omission | Q02 | [Q02-F06](annotations/Q02.json) | [SKILL.md:14-14](inputs/controlled/Q02/SKILL.md#L14) |
| parameter_omission | Q03 | [Q03-F04](annotations/Q03.json) | [SKILL.md:16-16](inputs/controlled/Q03/SKILL.md#L16); [SKILL.md:13-15](inputs/controlled/Q03/SKILL.md#L13) |
| parameter_omission | Q03 | [Q03-F06](annotations/Q03.json) | [SKILL.md:17-17](inputs/controlled/Q03/SKILL.md#L17); [SKILL.md:13-15](inputs/controlled/Q03/SKILL.md#L13) |
| parameter_omission | Q04 | [Q04-F04](annotations/Q04.json) | [references/workflow.md:11-11](inputs/controlled/Q04/references/workflow.md#L11); [references/workflow.md:9-9](inputs/controlled/Q04/references/workflow.md#L9); [references/workflow.md:15-15](inputs/controlled/Q04/references/workflow.md#L15); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8); [query.yaml:2-2](inputs/controlled/Q04/query.yaml#L2); [query.yaml:1-1](inputs/controlled/Q04/query.yaml#L1) |
| parameter_omission | Q04 | [Q04-F06](annotations/Q04.json) | [references/workflow.md:13-13](inputs/controlled/Q04/references/workflow.md#L13); [references/workflow.md:9-9](inputs/controlled/Q04/references/workflow.md#L9); [references/workflow.md:15-15](inputs/controlled/Q04/references/workflow.md#L15); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8); [query.yaml:3-3](inputs/controlled/Q04/query.yaml#L3); [query.yaml:1-1](inputs/controlled/Q04/query.yaml#L1) |
| parameter_omission | Q05 | [Q05-F04](annotations/Q05.json) | [SKILL.md:12-12](inputs/controlled/Q05/SKILL.md#L12) |
| parameter_omission | Q05 | [Q05-F06](annotations/Q05.json) | [SKILL.md:14-14](inputs/controlled/Q05/SKILL.md#L14) |
| parameter_omission | Q06 | [Q06-F04](annotations/Q06.json) | [SKILL.md:12-12](inputs/controlled/Q06/SKILL.md#L12) |
| parameter_omission | R02 | [R02-F06](annotations/R02.json) | [SKILL.md:124-130](inputs/upstream/playwright/SKILL.md#L124); [scripts/playwright_cli.sh:9-25](inputs/upstream/playwright/scripts/playwright_cli.sh#L9) |
| parameter_omission | R03 | [R03-F02](annotations/R03.json) | [SKILL.md:16-20](inputs/upstream/gh-fix-ci/SKILL.md#L16); [SKILL.md:32-38](inputs/upstream/gh-fix-ci/SKILL.md#L32) |
| parameter_omission | R06 | [R06-F06](annotations/R06.json) | [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:155-186](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L155) |
| parameter_scope | R02 | [R02-F09](annotations/R02.json) | [SKILL.md:132-137](inputs/upstream/playwright/SKILL.md#L132); [references/workflows.md:72-89](inputs/upstream/playwright/references/workflows.md#L72) |
| parameter_scope | R03 | [R03-F04](annotations/R03.json) | [SKILL.md:39-44](inputs/upstream/gh-fix-ci/SKILL.md#L39); [scripts/inspect_pr_checks.py:182-215](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L182) |
| parameter_scope | R04 | [R04-F02](annotations/R04.json) | [SKILL.md:70-98](inputs/upstream/netlify-deploy/SKILL.md#L70) |
| parameter_scope | R04 | [R04-F06](annotations/R04.json) | [SKILL.md:152-163](inputs/upstream/netlify-deploy/SKILL.md#L152); [SKILL.md:243-247](inputs/upstream/netlify-deploy/SKILL.md#L243); [references/netlify-toml.md:13-33](inputs/upstream/netlify-deploy/references/netlify-toml.md#L13) |
| parameter_scope | R05 | [R05-F04](annotations/R05.json) | [SKILL.md:40-50](inputs/upstream/linear/SKILL.md#L40) |
| parameter_scope | R05 | [R05-F05](annotations/R05.json) | [SKILL.md:46-50](inputs/upstream/linear/SKILL.md#L46) |
| parameter_scope | R06 | [R06-F03](annotations/R06.json) | [SKILL.md:18-22](inputs/upstream/transcribe/SKILL.md#L18) |
| parameter_scope | R06 | [R06-F08](annotations/R06.json) | [SKILL.md:24-26](inputs/upstream/transcribe/SKILL.md#L24); [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:234-239](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L234); [scripts/transcribe_diarize.py:101-123](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L101); [scripts/transcribe_diarize.py:263-272](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L263) |
| parameter_scope | R06 | [R06-F11](annotations/R06.json) | [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:169-186](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L169); [scripts/transcribe_diarize.py:252-264](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L252) |
| parameter_table | Q03 | [Q03-F03](annotations/Q03.json) | [SKILL.md:16-16](inputs/controlled/Q03/SKILL.md#L16); [SKILL.md:13-15](inputs/controlled/Q03/SKILL.md#L13) |
| parameter_table | Q03 | [Q03-F04](annotations/Q03.json) | [SKILL.md:16-16](inputs/controlled/Q03/SKILL.md#L16); [SKILL.md:13-15](inputs/controlled/Q03/SKILL.md#L13) |
| parameter_table | Q03 | [Q03-F05](annotations/Q03.json) | [SKILL.md:17-17](inputs/controlled/Q03/SKILL.md#L17); [SKILL.md:13-15](inputs/controlled/Q03/SKILL.md#L13) |
| parameter_table | Q03 | [Q03-F06](annotations/Q03.json) | [SKILL.md:17-17](inputs/controlled/Q03/SKILL.md#L17); [SKILL.md:13-15](inputs/controlled/Q03/SKILL.md#L13) |
| parameter_table | Q03 | [Q03-F10](annotations/Q03.json) | [SKILL.md:16-16](inputs/controlled/Q03/SKILL.md#L16); [SKILL.md:13-15](inputs/controlled/Q03/SKILL.md#L13); [SKILL.md:21-21](inputs/controlled/Q03/SKILL.md#L21) |
| precondition | F01 | [F01-F02](annotations/F01.json) | [SKILL.md:9-9](inputs/controlled/F01/SKILL.md#L9) |
| precondition | F02 | [F02-F02](annotations/F02.json) | [SKILL.md:8-8](inputs/controlled/F02/SKILL.md#L8) |
| precondition | F03 | [F03-F02](annotations/F03.json) | [SKILL.md:11-11](inputs/controlled/F03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| precondition | F04 | [F04-F02](annotations/F04.json) | [references/workflow.md:5-5](inputs/controlled/F04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| precondition | F05 | [F05-F02](annotations/F05.json) | [SKILL.md:9-9](inputs/controlled/F05/SKILL.md#L9) |
| precondition | F06 | [F06-F02](annotations/F06.json) | [SKILL.md:9-9](inputs/controlled/F06/SKILL.md#L9) |
| precondition | R02 | [R02-F02](annotations/R02.json) | [SKILL.md:12-32](inputs/upstream/playwright/SKILL.md#L12) |
| precondition | R03 | [R03-F01](annotations/R03.json) | [SKILL.md:29-31](inputs/upstream/gh-fix-ci/SKILL.md#L29) |
| precondition | R03 | [R03-F07](annotations/R03.json) | [SKILL.md:50-58](inputs/upstream/gh-fix-ci/SKILL.md#L50) |
| precondition | R04 | [R04-F01](annotations/R04.json) | [SKILL.md:30-36](inputs/upstream/netlify-deploy/SKILL.md#L30); [SKILL.md:52-66](inputs/upstream/netlify-deploy/SKILL.md#L52) |
| precondition | R05 | [R05-F01](annotations/R05.json) | [SKILL.md:14-20](inputs/upstream/linear/SKILL.md#L14) |
| precondition | R06 | [R06-F02](annotations/R06.json) | [SKILL.md:13-14](inputs/upstream/transcribe/SKILL.md#L13); [SKILL.md:39-42](inputs/upstream/transcribe/SKILL.md#L39) |
| prohibition | D01 | [D01-F08](annotations/D01.json) | [SKILL.md:15-15](inputs/controlled/D01/SKILL.md#L15) |
| prohibition | D01 | [D01-F09](annotations/D01.json) | [SKILL.md:16-16](inputs/controlled/D01/SKILL.md#L16) |
| prohibition | D02 | [D02-F08](annotations/D02.json) | [SKILL.md:14-14](inputs/controlled/D02/SKILL.md#L14) |
| prohibition | D02 | [D02-F09](annotations/D02.json) | [SKILL.md:16-16](inputs/controlled/D02/SKILL.md#L16) |
| prohibition | D03 | [D03-F08](annotations/D03.json) | [SKILL.md:17-17](inputs/controlled/D03/SKILL.md#L17); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| prohibition | D03 | [D03-F09](annotations/D03.json) | [SKILL.md:18-18](inputs/controlled/D03/SKILL.md#L18); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| prohibition | D04 | [D04-F08](annotations/D04.json) | [references/workflow.md:23-23](inputs/controlled/D04/references/workflow.md#L23); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8) |
| prohibition | D04 | [D04-F09](annotations/D04.json) | [references/workflow.md:25-25](inputs/controlled/D04/references/workflow.md#L25); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8) |
| prohibition | D05 | [D05-F08](annotations/D05.json) | [SKILL.md:15-15](inputs/controlled/D05/SKILL.md#L15) |
| prohibition | D05 | [D05-F09](annotations/D05.json) | [SKILL.md:16-16](inputs/controlled/D05/SKILL.md#L16) |
| prohibition | D06 | [D06-F08](annotations/D06.json) | [SKILL.md:15-15](inputs/controlled/D06/SKILL.md#L15) |
| prohibition | D06 | [D06-F09](annotations/D06.json) | [SKILL.md:16-16](inputs/controlled/D06/SKILL.md#L16) |
| prohibition | F01 | [F01-F09](annotations/F01.json) | [SKILL.md:15-15](inputs/controlled/F01/SKILL.md#L15) |
| prohibition | F02 | [F02-F09](annotations/F02.json) | [SKILL.md:14-14](inputs/controlled/F02/SKILL.md#L14) |
| prohibition | F03 | [F03-F09](annotations/F03.json) | [SKILL.md:17-17](inputs/controlled/F03/SKILL.md#L17); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| prohibition | F04 | [F04-F09](annotations/F04.json) | [references/workflow.md:19-19](inputs/controlled/F04/references/workflow.md#L19); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| prohibition | F05 | [F05-F09](annotations/F05.json) | [SKILL.md:15-15](inputs/controlled/F05/SKILL.md#L15) |
| prohibition | F06 | [F06-F09](annotations/F06.json) | [SKILL.md:15-15](inputs/controlled/F06/SKILL.md#L15) |
| prohibition | N01 | [N01-F07](annotations/N01.json) | [SKILL.md:14-14](inputs/controlled/N01/SKILL.md#L14) |
| prohibition | N02 | [N02-F07](annotations/N02.json) | [SKILL.md:14-14](inputs/controlled/N02/SKILL.md#L14) |
| prohibition | N03 | [N03-F07](annotations/N03.json) | [SKILL.md:16-16](inputs/controlled/N03/SKILL.md#L16); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| prohibition | N04 | [N04-F07](annotations/N04.json) | [references/workflow.md:17-17](inputs/controlled/N04/references/workflow.md#L17); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8) |
| prohibition | N05 | [N05-F07](annotations/N05.json) | [SKILL.md:14-14](inputs/controlled/N05/SKILL.md#L14) |
| prohibition | N06 | [N06-F07](annotations/N06.json) | [SKILL.md:14-14](inputs/controlled/N06/SKILL.md#L14) |
| prohibition | Q01 | [Q01-F08](annotations/Q01.json) | [SKILL.md:15-15](inputs/controlled/Q01/SKILL.md#L15) |
| prohibition | Q02 | [Q02-F08](annotations/Q02.json) | [SKILL.md:14-14](inputs/controlled/Q02/SKILL.md#L14) |
| prohibition | Q03 | [Q03-F08](annotations/Q03.json) | [SKILL.md:19-19](inputs/controlled/Q03/SKILL.md#L19) |
| prohibition | Q04 | [Q04-F08](annotations/Q04.json) | [references/workflow.md:17-17](inputs/controlled/Q04/references/workflow.md#L17); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8) |
| prohibition | Q05 | [Q05-F08](annotations/Q05.json) | [SKILL.md:15-15](inputs/controlled/Q05/SKILL.md#L15) |
| prohibition | Q06 | [Q06-F08](annotations/Q06.json) | [SKILL.md:15-15](inputs/controlled/Q06/SKILL.md#L15) |
| prohibition | R01 | [R01-F03](annotations/R01.json) | [SKILL.md:19-20](inputs/upstream/pdf/SKILL.md#L19) |
| prohibition | R02 | [R02-F01](annotations/R02.json) | [SKILL.md:9-10](inputs/upstream/playwright/SKILL.md#L9); [SKILL.md:122-130](inputs/upstream/playwright/SKILL.md#L122); [SKILL.md:57-62](inputs/upstream/playwright/SKILL.md#L57) |
| prohibition | R02 | [R02-F05](annotations/R02.json) | [SKILL.md:139-147](inputs/upstream/playwright/SKILL.md#L139) |
| prohibition | R03 | [R03-F06](annotations/R03.json) | [SKILL.md:47-49](inputs/upstream/gh-fix-ci/SKILL.md#L47); [scripts/inspect_pr_checks.py:244-257](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L244) |
| prohibition | R04 | [R04-F09](annotations/R04.json) | [SKILL.md:223-229](inputs/upstream/netlify-deploy/SKILL.md#L223); [SKILL.md:243-247](inputs/upstream/netlify-deploy/SKILL.md#L243); [references/cli-commands.md:82-96](inputs/upstream/netlify-deploy/references/cli-commands.md#L82) |
| prohibition | R06 | [R06-F02](annotations/R06.json) | [SKILL.md:13-14](inputs/upstream/transcribe/SKILL.md#L13); [SKILL.md:39-42](inputs/upstream/transcribe/SKILL.md#L39) |
| prohibition | R06 | [R06-F04](annotations/R06.json) | [SKILL.md:22-22](inputs/upstream/transcribe/SKILL.md#L22); [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:241-244](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L241) |
| quoted_example | D05 | [D05-F07](annotations/D05.json) | [SKILL.md:14-14](inputs/controlled/D05/SKILL.md#L14) |
| quoted_example | F05 | [F05-F10](annotations/F05.json) | [SKILL.md:16-16](inputs/controlled/F05/SKILL.md#L16) |
| quoted_example | N05 | [N05-F09](annotations/N05.json) | [SKILL.md:16-16](inputs/controlled/N05/SKILL.md#L16) |
| quoted_example | Q05 | [Q05-F11](annotations/Q05.json) | [SKILL.md:17-17](inputs/controlled/Q05/SKILL.md#L17) |
| retry | F01 | [F01-F04](annotations/F01.json) | [SKILL.md:10-10](inputs/controlled/F01/SKILL.md#L10) |
| retry | F02 | [F02-F04](annotations/F02.json) | [SKILL.md:10-10](inputs/controlled/F02/SKILL.md#L10) |
| retry | F03 | [F03-F04](annotations/F03.json) | [SKILL.md:12-12](inputs/controlled/F03/SKILL.md#L12); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| retry | F04 | [F04-F04](annotations/F04.json) | [references/workflow.md:8-8](inputs/controlled/F04/references/workflow.md#L8); [references/workflow.md:7-7](inputs/controlled/F04/references/workflow.md#L7); [references/workflow.md:11-11](inputs/controlled/F04/references/workflow.md#L11); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8); [retry.yaml:1-3](inputs/controlled/F04/retry.yaml#L1) |
| retry | F05 | [F05-F04](annotations/F05.json) | [SKILL.md:10-10](inputs/controlled/F05/SKILL.md#L10) |
| retry | F06 | [F06-F04](annotations/F06.json) | [SKILL.md:10-10](inputs/controlled/F06/SKILL.md#L10) |
| retry_boundaries | R02 | [R02-F04](annotations/R02.json) | [SKILL.md:80-89](inputs/upstream/playwright/SKILL.md#L80); [SKILL.md:132-137](inputs/upstream/playwright/SKILL.md#L132); [references/workflows.md:91-95](inputs/upstream/playwright/references/workflows.md#L91) |
| retry_boundaries | R03 | [R03-F04](annotations/R03.json) | [SKILL.md:39-44](inputs/upstream/gh-fix-ci/SKILL.md#L39); [scripts/inspect_pr_checks.py:182-215](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L182) |
| scope | D01 | [D01-F03](annotations/D01.json) | [SKILL.md:10-10](inputs/controlled/D01/SKILL.md#L10) |
| scope | D01 | [D01-F08](annotations/D01.json) | [SKILL.md:15-15](inputs/controlled/D01/SKILL.md#L15) |
| scope | D01 | [D01-F09](annotations/D01.json) | [SKILL.md:16-16](inputs/controlled/D01/SKILL.md#L16) |
| scope | D01 | [D01-F10](annotations/D01.json) | [SKILL.md:17-17](inputs/controlled/D01/SKILL.md#L17) |
| scope | D02 | [D02-F03](annotations/D02.json) | [SKILL.md:10-10](inputs/controlled/D02/SKILL.md#L10) |
| scope | D02 | [D02-F08](annotations/D02.json) | [SKILL.md:14-14](inputs/controlled/D02/SKILL.md#L14) |
| scope | D02 | [D02-F09](annotations/D02.json) | [SKILL.md:16-16](inputs/controlled/D02/SKILL.md#L16) |
| scope | D02 | [D02-F10](annotations/D02.json) | [SKILL.md:16-16](inputs/controlled/D02/SKILL.md#L16) |
| scope | D03 | [D03-F03](annotations/D03.json) | [SKILL.md:12-12](inputs/controlled/D03/SKILL.md#L12); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| scope | D03 | [D03-F08](annotations/D03.json) | [SKILL.md:17-17](inputs/controlled/D03/SKILL.md#L17); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| scope | D03 | [D03-F09](annotations/D03.json) | [SKILL.md:18-18](inputs/controlled/D03/SKILL.md#L18); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| scope | D03 | [D03-F10](annotations/D03.json) | [SKILL.md:19-19](inputs/controlled/D03/SKILL.md#L19); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| scope | D04 | [D04-F03](annotations/D04.json) | [references/workflow.md:7-7](inputs/controlled/D04/references/workflow.md#L7); [references/workflow.md:5-5](inputs/controlled/D04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8) |
| scope | D04 | [D04-F08](annotations/D04.json) | [references/workflow.md:23-23](inputs/controlled/D04/references/workflow.md#L23); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8) |
| scope | D04 | [D04-F09](annotations/D04.json) | [references/workflow.md:25-25](inputs/controlled/D04/references/workflow.md#L25); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8) |
| scope | D04 | [D04-F10](annotations/D04.json) | [references/workflow.md:27-27](inputs/controlled/D04/references/workflow.md#L27); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8) |
| scope | D05 | [D05-F03](annotations/D05.json) | [SKILL.md:10-10](inputs/controlled/D05/SKILL.md#L10) |
| scope | D05 | [D05-F08](annotations/D05.json) | [SKILL.md:15-15](inputs/controlled/D05/SKILL.md#L15) |
| scope | D05 | [D05-F09](annotations/D05.json) | [SKILL.md:16-16](inputs/controlled/D05/SKILL.md#L16) |
| scope | D05 | [D05-F10](annotations/D05.json) | [SKILL.md:17-17](inputs/controlled/D05/SKILL.md#L17) |
| scope | D06 | [D06-F03](annotations/D06.json) | [SKILL.md:10-10](inputs/controlled/D06/SKILL.md#L10) |
| scope | D06 | [D06-F08](annotations/D06.json) | [SKILL.md:15-15](inputs/controlled/D06/SKILL.md#L15) |
| scope | D06 | [D06-F09](annotations/D06.json) | [SKILL.md:16-16](inputs/controlled/D06/SKILL.md#L16) |
| scope | D06 | [D06-F10](annotations/D06.json) | [SKILL.md:17-17](inputs/controlled/D06/SKILL.md#L17) |
| scope | F01 | [F01-F06](annotations/F01.json) | [SKILL.md:12-12](inputs/controlled/F01/SKILL.md#L12) |
| scope | F01 | [F01-F09](annotations/F01.json) | [SKILL.md:15-15](inputs/controlled/F01/SKILL.md#L15) |
| scope | F02 | [F02-F06](annotations/F02.json) | [SKILL.md:12-12](inputs/controlled/F02/SKILL.md#L12) |
| scope | F02 | [F02-F09](annotations/F02.json) | [SKILL.md:14-14](inputs/controlled/F02/SKILL.md#L14) |
| scope | F03 | [F03-F06](annotations/F03.json) | [SKILL.md:14-14](inputs/controlled/F03/SKILL.md#L14); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| scope | F03 | [F03-F09](annotations/F03.json) | [SKILL.md:17-17](inputs/controlled/F03/SKILL.md#L17); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| scope | F04 | [F04-F06](annotations/F04.json) | [references/workflow.md:13-13](inputs/controlled/F04/references/workflow.md#L13); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| scope | F04 | [F04-F09](annotations/F04.json) | [references/workflow.md:19-19](inputs/controlled/F04/references/workflow.md#L19); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| scope | F05 | [F05-F06](annotations/F05.json) | [SKILL.md:12-12](inputs/controlled/F05/SKILL.md#L12) |
| scope | F05 | [F05-F09](annotations/F05.json) | [SKILL.md:15-15](inputs/controlled/F05/SKILL.md#L15) |
| scope | F06 | [F06-F06](annotations/F06.json) | [SKILL.md:12-12](inputs/controlled/F06/SKILL.md#L12) |
| scope | F06 | [F06-F09](annotations/F06.json) | [SKILL.md:15-15](inputs/controlled/F06/SKILL.md#L15) |
| scope | N01 | [N01-F03](annotations/N01.json) | [SKILL.md:9-9](inputs/controlled/N01/SKILL.md#L9); [SKILL.md:10-10](inputs/controlled/N01/SKILL.md#L10) |
| scope | N01 | [N01-F07](annotations/N01.json) | [SKILL.md:14-14](inputs/controlled/N01/SKILL.md#L14) |
| scope | N02 | [N02-F03](annotations/N02.json) | [SKILL.md:8-8](inputs/controlled/N02/SKILL.md#L8); [SKILL.md:10-10](inputs/controlled/N02/SKILL.md#L10) |
| scope | N02 | [N02-F07](annotations/N02.json) | [SKILL.md:14-14](inputs/controlled/N02/SKILL.md#L14) |
| scope | N03 | [N03-F03](annotations/N03.json) | [SKILL.md:11-11](inputs/controlled/N03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7); [SKILL.md:12-12](inputs/controlled/N03/SKILL.md#L12) |
| scope | N03 | [N03-F07](annotations/N03.json) | [SKILL.md:16-16](inputs/controlled/N03/SKILL.md#L16); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| scope | N04 | [N04-F03](annotations/N04.json) | [references/workflow.md:6-6](inputs/controlled/N04/references/workflow.md#L6); [references/workflow.md:5-5](inputs/controlled/N04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8); [references/workflow.md:7-7](inputs/controlled/N04/references/workflow.md#L7) |
| scope | N04 | [N04-F07](annotations/N04.json) | [references/workflow.md:17-17](inputs/controlled/N04/references/workflow.md#L17); [SKILL.md:8-8](inputs/controlled/N04/SKILL.md#L8) |
| scope | N05 | [N05-F03](annotations/N05.json) | [SKILL.md:9-9](inputs/controlled/N05/SKILL.md#L9); [SKILL.md:10-10](inputs/controlled/N05/SKILL.md#L10) |
| scope | N05 | [N05-F07](annotations/N05.json) | [SKILL.md:14-14](inputs/controlled/N05/SKILL.md#L14) |
| scope | N06 | [N06-F03](annotations/N06.json) | [SKILL.md:9-9](inputs/controlled/N06/SKILL.md#L9); [SKILL.md:10-10](inputs/controlled/N06/SKILL.md#L10) |
| scope | N06 | [N06-F07](annotations/N06.json) | [SKILL.md:14-14](inputs/controlled/N06/SKILL.md#L14) |
| scope | Q01 | [Q01-F03](annotations/Q01.json) | [SKILL.md:11-11](inputs/controlled/Q01/SKILL.md#L11) |
| scope | Q01 | [Q01-F08](annotations/Q01.json) | [SKILL.md:15-15](inputs/controlled/Q01/SKILL.md#L15) |
| scope | Q02 | [Q02-F03](annotations/Q02.json) | [SKILL.md:10-10](inputs/controlled/Q02/SKILL.md#L10) |
| scope | Q02 | [Q02-F08](annotations/Q02.json) | [SKILL.md:14-14](inputs/controlled/Q02/SKILL.md#L14) |
| scope | Q03 | [Q03-F03](annotations/Q03.json) | [SKILL.md:16-16](inputs/controlled/Q03/SKILL.md#L16); [SKILL.md:13-15](inputs/controlled/Q03/SKILL.md#L13) |
| scope | Q03 | [Q03-F08](annotations/Q03.json) | [SKILL.md:19-19](inputs/controlled/Q03/SKILL.md#L19) |
| scope | Q04 | [Q04-F03](annotations/Q04.json) | [references/workflow.md:10-10](inputs/controlled/Q04/references/workflow.md#L10); [references/workflow.md:9-9](inputs/controlled/Q04/references/workflow.md#L9); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8) |
| scope | Q04 | [Q04-F08](annotations/Q04.json) | [references/workflow.md:17-17](inputs/controlled/Q04/references/workflow.md#L17); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8) |
| scope | Q05 | [Q05-F03](annotations/Q05.json) | [SKILL.md:11-11](inputs/controlled/Q05/SKILL.md#L11) |
| scope | Q05 | [Q05-F08](annotations/Q05.json) | [SKILL.md:15-15](inputs/controlled/Q05/SKILL.md#L15) |
| scope | Q06 | [Q06-F03](annotations/Q06.json) | [SKILL.md:11-11](inputs/controlled/Q06/SKILL.md#L11) |
| scope | Q06 | [Q06-F08](annotations/Q06.json) | [SKILL.md:15-15](inputs/controlled/Q06/SKILL.md#L15) |
| step_table | D03 | [D03-F01](annotations/D03.json) | [SKILL.md:10-10](inputs/controlled/D03/SKILL.md#L10); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| step_table | D03 | [D03-F02](annotations/D03.json) | [SKILL.md:11-11](inputs/controlled/D03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [scripts/convert.py:5-10](inputs/controlled/D03/scripts/convert.py#L5) |
| step_table | D03 | [D03-F03](annotations/D03.json) | [SKILL.md:12-12](inputs/controlled/D03/SKILL.md#L12); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| step_table | D03 | [D03-F04](annotations/D03.json) | [SKILL.md:11-11](inputs/controlled/D03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [SKILL.md:13-13](inputs/controlled/D03/SKILL.md#L13); [scripts/convert.py:5-10](inputs/controlled/D03/scripts/convert.py#L5) |
| step_table | D03 | [D03-F05](annotations/D03.json) | [SKILL.md:14-14](inputs/controlled/D03/SKILL.md#L14); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [SKILL.md:23-25](inputs/controlled/D03/SKILL.md#L23); [scripts/package.py:7-13](inputs/controlled/D03/scripts/package.py#L7) |
| step_table | D03 | [D03-F06](annotations/D03.json) | [SKILL.md:10-10](inputs/controlled/D03/SKILL.md#L10); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [SKILL.md:15-15](inputs/controlled/D03/SKILL.md#L15) |
| step_table | D03 | [D03-F07](annotations/D03.json) | [SKILL.md:16-16](inputs/controlled/D03/SKILL.md#L16); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| step_table | D03 | [D03-F08](annotations/D03.json) | [SKILL.md:17-17](inputs/controlled/D03/SKILL.md#L17); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| step_table | D03 | [D03-F09](annotations/D03.json) | [SKILL.md:18-18](inputs/controlled/D03/SKILL.md#L18); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| step_table | D03 | [D03-F10](annotations/D03.json) | [SKILL.md:19-19](inputs/controlled/D03/SKILL.md#L19); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| step_table | F03 | [F03-F01](annotations/F03.json) | [SKILL.md:10-10](inputs/controlled/F03/SKILL.md#L10); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| step_table | F03 | [F03-F02](annotations/F03.json) | [SKILL.md:11-11](inputs/controlled/F03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| step_table | F03 | [F03-F03](annotations/F03.json) | [SKILL.md:10-10](inputs/controlled/F03/SKILL.md#L10); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7); [SKILL.md:11-11](inputs/controlled/F03/SKILL.md#L11) |
| step_table | F03 | [F03-F04](annotations/F03.json) | [SKILL.md:12-12](inputs/controlled/F03/SKILL.md#L12); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| step_table | F03 | [F03-F05](annotations/F03.json) | [SKILL.md:13-13](inputs/controlled/F03/SKILL.md#L13); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| step_table | F03 | [F03-F06](annotations/F03.json) | [SKILL.md:14-14](inputs/controlled/F03/SKILL.md#L14); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| step_table | F03 | [F03-F07](annotations/F03.json) | [SKILL.md:15-15](inputs/controlled/F03/SKILL.md#L15); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| step_table | F03 | [F03-F08](annotations/F03.json) | [SKILL.md:16-16](inputs/controlled/F03/SKILL.md#L16); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| step_table | F03 | [F03-F09](annotations/F03.json) | [SKILL.md:17-17](inputs/controlled/F03/SKILL.md#L17); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| step_table | F03 | [F03-F10](annotations/F03.json) | [SKILL.md:18-18](inputs/controlled/F03/SKILL.md#L18); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| step_table | N03 | [N03-F01](annotations/N03.json) | [SKILL.md:10-10](inputs/controlled/N03/SKILL.md#L10); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| step_table | N03 | [N03-F02](annotations/N03.json) | [SKILL.md:11-11](inputs/controlled/N03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7); [SKILL.md:12-12](inputs/controlled/N03/SKILL.md#L12) |
| step_table | N03 | [N03-F03](annotations/N03.json) | [SKILL.md:11-11](inputs/controlled/N03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7); [SKILL.md:12-12](inputs/controlled/N03/SKILL.md#L12) |
| step_table | N03 | [N03-F04](annotations/N03.json) | [SKILL.md:13-13](inputs/controlled/N03/SKILL.md#L13); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| step_table | N03 | [N03-F05](annotations/N03.json) | [SKILL.md:14-14](inputs/controlled/N03/SKILL.md#L14); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| step_table | N03 | [N03-F06](annotations/N03.json) | [SKILL.md:15-15](inputs/controlled/N03/SKILL.md#L15); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| step_table | N03 | [N03-F07](annotations/N03.json) | [SKILL.md:16-16](inputs/controlled/N03/SKILL.md#L16); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| step_table | N03 | [N03-F08](annotations/N03.json) | [SKILL.md:17-17](inputs/controlled/N03/SKILL.md#L17); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| step_table | N03 | [N03-F09](annotations/N03.json) | [SKILL.md:18-18](inputs/controlled/N03/SKILL.md#L18); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| stop_condition | F01 | [F01-F07](annotations/F01.json) | [SKILL.md:13-13](inputs/controlled/F01/SKILL.md#L13) |
| stop_condition | F01 | [F01-F08](annotations/F01.json) | [SKILL.md:14-14](inputs/controlled/F01/SKILL.md#L14) |
| stop_condition | F02 | [F02-F07](annotations/F02.json) | [SKILL.md:12-12](inputs/controlled/F02/SKILL.md#L12) |
| stop_condition | F02 | [F02-F08](annotations/F02.json) | [SKILL.md:14-14](inputs/controlled/F02/SKILL.md#L14) |
| stop_condition | F03 | [F03-F07](annotations/F03.json) | [SKILL.md:15-15](inputs/controlled/F03/SKILL.md#L15); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| stop_condition | F03 | [F03-F08](annotations/F03.json) | [SKILL.md:16-16](inputs/controlled/F03/SKILL.md#L16); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| stop_condition | F04 | [F04-F07](annotations/F04.json) | [references/workflow.md:15-15](inputs/controlled/F04/references/workflow.md#L15); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| stop_condition | F04 | [F04-F08](annotations/F04.json) | [references/workflow.md:17-17](inputs/controlled/F04/references/workflow.md#L17); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| stop_condition | F05 | [F05-F07](annotations/F05.json) | [SKILL.md:13-13](inputs/controlled/F05/SKILL.md#L13) |
| stop_condition | F05 | [F05-F08](annotations/F05.json) | [SKILL.md:14-14](inputs/controlled/F05/SKILL.md#L14) |
| stop_condition | F06 | [F06-F07](annotations/F06.json) | [SKILL.md:13-13](inputs/controlled/F06/SKILL.md#L13) |
| stop_condition | F06 | [F06-F08](annotations/F06.json) | [SKILL.md:14-14](inputs/controlled/F06/SKILL.md#L14) |
| stop_condition | R01 | [R01-F05](annotations/R01.json) | [SKILL.md:20-20](inputs/upstream/pdf/SKILL.md#L20); [SKILL.md:64-66](inputs/upstream/pdf/SKILL.md#L64) |
| stop_condition | R02 | [R02-F02](annotations/R02.json) | [SKILL.md:12-32](inputs/upstream/playwright/SKILL.md#L12) |
| stop_condition | R03 | [R03-F01](annotations/R03.json) | [SKILL.md:29-31](inputs/upstream/gh-fix-ci/SKILL.md#L29) |
| stop_condition | R03 | [R03-F09](annotations/R03.json) | [SKILL.md:64-64](inputs/upstream/gh-fix-ci/SKILL.md#L64); [scripts/inspect_pr_checks.py:110-135](inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py#L110) |
| stop_condition | R04 | [R04-F01](annotations/R04.json) | [SKILL.md:30-36](inputs/upstream/netlify-deploy/SKILL.md#L30); [SKILL.md:52-66](inputs/upstream/netlify-deploy/SKILL.md#L52) |
| stop_condition | R05 | [R05-F02](annotations/R05.json) | [SKILL.md:22-33](inputs/upstream/linear/SKILL.md#L22) |
| stop_condition | R06 | [R06-F04](annotations/R06.json) | [SKILL.md:22-22](inputs/upstream/transcribe/SKILL.md#L22); [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:241-244](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L241) |
| stop_condition | R06 | [R06-F07](annotations/R06.json) | [SKILL.md:14-14](inputs/upstream/transcribe/SKILL.md#L14); [scripts/transcribe_diarize.py:33-40](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L33); [scripts/transcribe_diarize.py:246-264](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L246) |
| suspicious_behavior_preserved | R04 | [R04-F08](annotations/R04.json) | [SKILL.md:213-220](inputs/upstream/netlify-deploy/SKILL.md#L213) |
| table_headers | D03 | [D03-F01](annotations/D03.json) | [SKILL.md:10-10](inputs/controlled/D03/SKILL.md#L10); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| table_headers | D03 | [D03-F02](annotations/D03.json) | [SKILL.md:11-11](inputs/controlled/D03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [scripts/convert.py:5-10](inputs/controlled/D03/scripts/convert.py#L5) |
| table_headers | D03 | [D03-F03](annotations/D03.json) | [SKILL.md:12-12](inputs/controlled/D03/SKILL.md#L12); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| table_headers | D03 | [D03-F04](annotations/D03.json) | [SKILL.md:11-11](inputs/controlled/D03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [SKILL.md:13-13](inputs/controlled/D03/SKILL.md#L13); [scripts/convert.py:5-10](inputs/controlled/D03/scripts/convert.py#L5) |
| table_headers | D03 | [D03-F05](annotations/D03.json) | [SKILL.md:14-14](inputs/controlled/D03/SKILL.md#L14); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [SKILL.md:23-25](inputs/controlled/D03/SKILL.md#L23); [scripts/package.py:7-13](inputs/controlled/D03/scripts/package.py#L7) |
| table_headers | D03 | [D03-F06](annotations/D03.json) | [SKILL.md:10-10](inputs/controlled/D03/SKILL.md#L10); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7); [SKILL.md:15-15](inputs/controlled/D03/SKILL.md#L15) |
| table_headers | D03 | [D03-F07](annotations/D03.json) | [SKILL.md:16-16](inputs/controlled/D03/SKILL.md#L16); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| table_headers | D03 | [D03-F08](annotations/D03.json) | [SKILL.md:17-17](inputs/controlled/D03/SKILL.md#L17); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| table_headers | D03 | [D03-F09](annotations/D03.json) | [SKILL.md:18-18](inputs/controlled/D03/SKILL.md#L18); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| table_headers | D03 | [D03-F10](annotations/D03.json) | [SKILL.md:19-19](inputs/controlled/D03/SKILL.md#L19); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| table_headers | F03 | [F03-F01](annotations/F03.json) | [SKILL.md:10-10](inputs/controlled/F03/SKILL.md#L10); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| table_headers | F03 | [F03-F02](annotations/F03.json) | [SKILL.md:11-11](inputs/controlled/F03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| table_headers | F03 | [F03-F03](annotations/F03.json) | [SKILL.md:10-10](inputs/controlled/F03/SKILL.md#L10); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7); [SKILL.md:11-11](inputs/controlled/F03/SKILL.md#L11) |
| table_headers | F03 | [F03-F04](annotations/F03.json) | [SKILL.md:12-12](inputs/controlled/F03/SKILL.md#L12); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| table_headers | F03 | [F03-F05](annotations/F03.json) | [SKILL.md:13-13](inputs/controlled/F03/SKILL.md#L13); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| table_headers | F03 | [F03-F06](annotations/F03.json) | [SKILL.md:14-14](inputs/controlled/F03/SKILL.md#L14); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| table_headers | F03 | [F03-F07](annotations/F03.json) | [SKILL.md:15-15](inputs/controlled/F03/SKILL.md#L15); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| table_headers | F03 | [F03-F08](annotations/F03.json) | [SKILL.md:16-16](inputs/controlled/F03/SKILL.md#L16); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| table_headers | F03 | [F03-F09](annotations/F03.json) | [SKILL.md:17-17](inputs/controlled/F03/SKILL.md#L17); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| table_headers | F03 | [F03-F10](annotations/F03.json) | [SKILL.md:18-18](inputs/controlled/F03/SKILL.md#L18); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| table_headers | N03 | [N03-F01](annotations/N03.json) | [SKILL.md:10-10](inputs/controlled/N03/SKILL.md#L10); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| table_headers | N03 | [N03-F02](annotations/N03.json) | [SKILL.md:11-11](inputs/controlled/N03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7); [SKILL.md:12-12](inputs/controlled/N03/SKILL.md#L12) |
| table_headers | N03 | [N03-F03](annotations/N03.json) | [SKILL.md:11-11](inputs/controlled/N03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7); [SKILL.md:12-12](inputs/controlled/N03/SKILL.md#L12) |
| table_headers | N03 | [N03-F04](annotations/N03.json) | [SKILL.md:13-13](inputs/controlled/N03/SKILL.md#L13); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| table_headers | N03 | [N03-F05](annotations/N03.json) | [SKILL.md:14-14](inputs/controlled/N03/SKILL.md#L14); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| table_headers | N03 | [N03-F06](annotations/N03.json) | [SKILL.md:15-15](inputs/controlled/N03/SKILL.md#L15); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| table_headers | N03 | [N03-F07](annotations/N03.json) | [SKILL.md:16-16](inputs/controlled/N03/SKILL.md#L16); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| table_headers | N03 | [N03-F08](annotations/N03.json) | [SKILL.md:17-17](inputs/controlled/N03/SKILL.md#L17); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| table_headers | N03 | [N03-F09](annotations/N03.json) | [SKILL.md:18-18](inputs/controlled/N03/SKILL.md#L18); [SKILL.md:7-9](inputs/controlled/N03/SKILL.md#L7) |
| table_headers | Q03 | [Q03-F03](annotations/Q03.json) | [SKILL.md:16-16](inputs/controlled/Q03/SKILL.md#L16); [SKILL.md:13-15](inputs/controlled/Q03/SKILL.md#L13) |
| table_headers | Q03 | [Q03-F04](annotations/Q03.json) | [SKILL.md:16-16](inputs/controlled/Q03/SKILL.md#L16); [SKILL.md:13-15](inputs/controlled/Q03/SKILL.md#L13) |
| table_headers | Q03 | [Q03-F05](annotations/Q03.json) | [SKILL.md:17-17](inputs/controlled/Q03/SKILL.md#L17); [SKILL.md:13-15](inputs/controlled/Q03/SKILL.md#L13) |
| table_headers | Q03 | [Q03-F06](annotations/Q03.json) | [SKILL.md:17-17](inputs/controlled/Q03/SKILL.md#L17); [SKILL.md:13-15](inputs/controlled/Q03/SKILL.md#L13) |
| table_headers | Q03 | [Q03-F10](annotations/Q03.json) | [SKILL.md:16-16](inputs/controlled/Q03/SKILL.md#L16); [SKILL.md:13-15](inputs/controlled/Q03/SKILL.md#L13); [SKILL.md:21-21](inputs/controlled/Q03/SKILL.md#L21) |
| tool_priority | F01 | [F01-F02](annotations/F01.json) | [SKILL.md:9-9](inputs/controlled/F01/SKILL.md#L9) |
| tool_priority | F02 | [F02-F02](annotations/F02.json) | [SKILL.md:8-8](inputs/controlled/F02/SKILL.md#L8) |
| tool_priority | F03 | [F03-F02](annotations/F03.json) | [SKILL.md:11-11](inputs/controlled/F03/SKILL.md#L11); [SKILL.md:7-9](inputs/controlled/F03/SKILL.md#L7) |
| tool_priority | F04 | [F04-F02](annotations/F04.json) | [references/workflow.md:5-5](inputs/controlled/F04/references/workflow.md#L5); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8) |
| tool_priority | F05 | [F05-F02](annotations/F05.json) | [SKILL.md:9-9](inputs/controlled/F05/SKILL.md#L9) |
| tool_priority | F06 | [F06-F02](annotations/F06.json) | [SKILL.md:9-9](inputs/controlled/F06/SKILL.md#L9) |
| tool_priority | R01 | [R01-F01](annotations/R01.json) | [SKILL.md:14-20](inputs/upstream/pdf/SKILL.md#L14) |
| tool_priority | R02 | [R02-F01](annotations/R02.json) | [SKILL.md:9-10](inputs/upstream/playwright/SKILL.md#L9); [SKILL.md:122-130](inputs/upstream/playwright/SKILL.md#L122); [SKILL.md:57-62](inputs/upstream/playwright/SKILL.md#L57) |
| unresolved_scope | D01 | [D01-F10](annotations/D01.json) | [SKILL.md:17-17](inputs/controlled/D01/SKILL.md#L17) |
| unresolved_scope | D02 | [D02-F10](annotations/D02.json) | [SKILL.md:16-16](inputs/controlled/D02/SKILL.md#L16) |
| unresolved_scope | D03 | [D03-F10](annotations/D03.json) | [SKILL.md:19-19](inputs/controlled/D03/SKILL.md#L19); [SKILL.md:7-9](inputs/controlled/D03/SKILL.md#L7) |
| unresolved_scope | D04 | [D04-F10](annotations/D04.json) | [references/workflow.md:27-27](inputs/controlled/D04/references/workflow.md#L27); [SKILL.md:8-8](inputs/controlled/D04/SKILL.md#L8) |
| unresolved_scope | D05 | [D05-F10](annotations/D05.json) | [SKILL.md:17-17](inputs/controlled/D05/SKILL.md#L17) |
| unresolved_scope | D06 | [D06-F10](annotations/D06.json) | [SKILL.md:17-17](inputs/controlled/D06/SKILL.md#L17) |
| unresolved_scope | R06 | [R06-F09](annotations/R06.json) | [SKILL.md:80-81](inputs/upstream/transcribe/SKILL.md#L80); [references/api.md:3-6](inputs/upstream/transcribe/references/api.md#L3); [scripts/transcribe_diarize.py:18-19](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L18); [scripts/transcribe_diarize.py:145-152](inputs/upstream/transcribe/scripts/transcribe_diarize.py#L145) |
| yaml | F04 | [F04-F04](annotations/F04.json) | [references/workflow.md:8-8](inputs/controlled/F04/references/workflow.md#L8); [references/workflow.md:7-7](inputs/controlled/F04/references/workflow.md#L7); [references/workflow.md:11-11](inputs/controlled/F04/references/workflow.md#L11); [SKILL.md:8-8](inputs/controlled/F04/SKILL.md#L8); [retry.yaml:1-3](inputs/controlled/F04/retry.yaml#L1) |
| yaml | Q04 | [Q04-F04](annotations/Q04.json) | [references/workflow.md:11-11](inputs/controlled/Q04/references/workflow.md#L11); [references/workflow.md:9-9](inputs/controlled/Q04/references/workflow.md#L9); [references/workflow.md:15-15](inputs/controlled/Q04/references/workflow.md#L15); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8); [query.yaml:2-2](inputs/controlled/Q04/query.yaml#L2); [query.yaml:1-1](inputs/controlled/Q04/query.yaml#L1) |
| yaml | Q04 | [Q04-F06](annotations/Q04.json) | [references/workflow.md:13-13](inputs/controlled/Q04/references/workflow.md#L13); [references/workflow.md:9-9](inputs/controlled/Q04/references/workflow.md#L9); [references/workflow.md:15-15](inputs/controlled/Q04/references/workflow.md#L15); [SKILL.md:8-8](inputs/controlled/Q04/SKILL.md#L8); [query.yaml:3-3](inputs/controlled/Q04/query.yaml#L3); [query.yaml:1-1](inputs/controlled/Q04/query.yaml#L1) |
