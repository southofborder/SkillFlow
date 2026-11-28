# Basic data propagation records

**These records describe static possible behavior under the shared abstract runtime contract, not execution logs. complete means only that solving finished under the contract, not that the model actually observed this content. Default observations and explicit exceptions jointly constrain analysis. Fixed ordering or absence of a contract citation does not establish an observed runtime fact. Entry and exit states retain computation and audit evidence, rather than complete historical environments. An omitted binding does not establish deletion or an empty value.**

Shared contract: `skillflow-abstract-runtime-v14`; SHA-256: `3c5e26ebc288fbba41176d1a9e3b7eef1132f5aacc23fe69a3535665f5b711f9`.

Solver status: `incomplete`.

IR record coverage: 18 / 62.

[Local visual review](report.html) · [Data](data.json) · [Operation records](records.json) · [Sink list](sinks.json)

D labels are report-local short names. Input/output indexes refer to atomic-operation arguments, not original IR operands. Control slots determine inclusion or observation and are not delivered payload. Candidate sets do not imply simultaneous occurrence; possible does not imply complete plaintext inclusion. This stage makes no risk, necessity or DOE judgment. Read scope, model observation, explicit selection and actual arguments are reviewed separately; a tool boundary does not imply networking.

[Frozen runtime contract text](../../../../../experiments/doe/runs/document-guided-google-search-retry-high-20261125-161918/source/inputs/runtime-contract.json) (runtime_contract); Expand the audit section below for individual evidence.

## Receiving and storage boundaries

Included positions: 1 operation positions; per-element candidate groups show arguments separately, using existing scope coordinates.

Levels describe boundary properties only: 0 task-local temporary, 1 task-local persistent, 2 another principal/shared, 3 public. They do not measure sensitivity, necessity or final risk. Coverage identifies unevaluated operations; empty arguments do not establish absence of unmodeled content.

| IR / step | Included | Type / level | Target, access / retention | Actual arguments by slot | Rationale and property evidence |
|---|---|---|---|---|---|
| ir_007 / 1.1 | Included | network_send / 2 | google_search_api · remote: https://www.googleapis.com/customsearch/v1 · recipient / Retention period not modeled | 0: D027; 1: D013, D026 | Another recipient or cross-principal sharing; skill/scripts/search.py:7-14, EM12 |

<details><summary>Complete source</summary>

<pre>{
  &quot;files&quot;: [
    {
      &quot;content&quot;: &quot;---\nname: google-search\ndescription: Search the web using Google Custom Search Engine (PSE). Use this when you need live information, documentation, or to research topics and the built-in web_search is unavailable.\n---\n\n# Google Search Skill\n\nThis skill allows OpenClaw agents to perform web searches via Google&#x27;s Custom Search API (PSE).\n\n## Setup\n\n1.  **Google Cloud Console:** Create a project and enable the \&quot;Custom Search API\&quot;.\n2.  **API Key:** Generate an API Key.\n3.  **Search Engine ID (CX):** Create a Programmable Search Engine at [cse.google.com](https://cse.google.com/cse/all), and get your CX ID.\n4.  **Environment:** Store your credentials in a `.env` file in your workspace:\n    ```\n    GOOGLE_API_KEY=your_key_here\n    GOOGLE_CSE_ID=your_cx_id_here\n    ```\n\n## Workflow\n... (rest of file)\n\n## Example Usage\n\n```bash\nGOOGLE_API_KEY=xxx GOOGLE_CSE_ID=yyy python3 skills/google-search/scripts/search.py \&quot;OpenClaw documentation\&quot;\n```\n&quot;,
      &quot;path&quot;: &quot;SKILL.md&quot;,
      &quot;sha256&quot;: &quot;d9600f3dc7af3761e2b2f421e05e78238f1f11d2e22cad0a35160bb1697c11a2&quot;
    },
    {
      &quot;content&quot;: &quot;import sys\nimport json\nimport requests\nimport os\n\ndef google_search(query, api_key, cse_id, num_results=5):\n    url = \&quot;https://www.googleapis.com/customsearch/v1\&quot;\n    params = {\n        &#x27;q&#x27;: query,\n        &#x27;key&#x27;: api_key,\n        &#x27;cx&#x27;: cse_id,\n        &#x27;num&#x27;: num_results\n    }\n    response = requests.get(url, params=params)\n    response.raise_for_status()\n    return response.json()\n\nif __name__ == \&quot;__main__\&quot;:\n    if len(sys.argv) &lt; 2:\n        print(\&quot;Usage: python google_search.py &lt;query&gt; [num_results]\&quot;)\n        sys.exit(1)\n\n    query = sys.argv[1]\n    num_results = int(sys.argv[2]) if len(sys.argv) &gt; 2 else 5\n    \n    # We will pass these via env vars for security\n    api_key = os.getenv(\&quot;GOOGLE_API_KEY\&quot;)\n    cse_id = os.getenv(\&quot;GOOGLE_CSE_ID\&quot;)\n\n    if not api_key or not cse_id:\n        print(\&quot;Error: GOOGLE_API_KEY and GOOGLE_CSE_ID must be set in environment.\&quot;)\n        sys.exit(1)\n\n    try:\n        results = google_search(query, api_key, cse_id, num_results)\n        print(json.dumps(results, indent=2))\n    except Exception as e:\n        print(f\&quot;Error: {str(e)}\&quot;)\n        sys.exit(1)\n&quot;,
      &quot;path&quot;: &quot;scripts/search.py&quot;,
      &quot;sha256&quot;: &quot;bebf186b146545beac53401f102c82188dd5a3c9c9bf1a77d31fe672ac53a26b&quot;
    }
  ],
  &quot;source_sha256&quot;: &quot;42837801b8ffa77e15a5b45e7742489a2d30dfe1d33bb8d3292f106c95a99b20&quot;
}</pre>

</details>

<details><summary>Coverage and diagnostics</summary>

<pre>{
  &quot;boundary_coverage&quot;: [
    {
      &quot;boundary&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;exposure_level&quot;: 2,
        &quot;instruction_id&quot;: &quot;ir_007&quot;,
        &quot;op_index&quot;: 0,
        &quot;scope&quot;: null,
        &quot;sink_type&quot;: &quot;network_send&quot;,
        &quot;target&quot;: &quot;google_search_api&quot;
      },
      &quot;reason&quot;: &quot;An actual static operation record resolves this boundary.&quot;,
      &quot;status&quot;: &quot;resolved&quot;
    },
    {
      &quot;boundary&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;exposure_level&quot;: 2,
        &quot;instruction_id&quot;: &quot;ir_047&quot;,
        &quot;op_index&quot;: 0,
        &quot;scope&quot;: null,
        &quot;sink_type&quot;: &quot;network_send&quot;,
        &quot;target&quot;: &quot;google_search_api&quot;
      },
      &quot;reason&quot;: &quot;No evaluated instruction record resolves this declared boundary; this is not an empty or safe payload.&quot;,
      &quot;status&quot;: &quot;unresolved&quot;
    },
    {
      &quot;boundary&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;exposure_level&quot;: 2,
        &quot;instruction_id&quot;: &quot;ir_055&quot;,
        &quot;op_index&quot;: 0,
        &quot;scope&quot;: null,
        &quot;sink_type&quot;: &quot;external_tool&quot;,
        &quot;target&quot;: &quot;stdout&quot;
      },
      &quot;reason&quot;: &quot;No evaluated instruction record resolves this declared boundary; this is not an empty or safe payload.&quot;,
      &quot;status&quot;: &quot;unresolved&quot;
    }
  ],
  &quot;coverage&quot;: {
    &quot;ir_001&quot;: &quot;processed&quot;,
    &quot;ir_002&quot;: &quot;processed_with_placeholder&quot;,
    &quot;ir_003&quot;: &quot;processed&quot;,
    &quot;ir_004&quot;: &quot;processed&quot;,
    &quot;ir_005&quot;: &quot;processed&quot;,
    &quot;ir_006&quot;: &quot;processed&quot;,
    &quot;ir_007&quot;: &quot;processed_with_placeholder&quot;,
    &quot;ir_008&quot;: &quot;processed&quot;,
    &quot;ir_009&quot;: &quot;processed&quot;,
    &quot;ir_010&quot;: &quot;unmodeled&quot;,
    &quot;ir_011&quot;: &quot;blocked&quot;,
    &quot;ir_012&quot;: &quot;blocked&quot;,
    &quot;ir_013&quot;: &quot;blocked&quot;,
    &quot;ir_014&quot;: &quot;blocked&quot;,
    &quot;ir_015&quot;: &quot;blocked&quot;,
    &quot;ir_016&quot;: &quot;blocked&quot;,
    &quot;ir_017&quot;: &quot;processed_with_placeholder&quot;,
    &quot;ir_018&quot;: &quot;processed&quot;,
    &quot;ir_019&quot;: &quot;processed_with_placeholder&quot;,
    &quot;ir_020&quot;: &quot;processed&quot;,
    &quot;ir_021&quot;: &quot;processed&quot;,
    &quot;ir_022&quot;: &quot;processed&quot;,
    &quot;ir_023&quot;: &quot;processed&quot;,
    &quot;ir_024&quot;: &quot;processed&quot;,
    &quot;ir_025&quot;: &quot;processed&quot;,
    &quot;ir_026&quot;: &quot;unmodeled&quot;,
    &quot;ir_027&quot;: &quot;blocked&quot;,
    &quot;ir_028&quot;: &quot;blocked&quot;,
    &quot;ir_029&quot;: &quot;blocked&quot;,
    &quot;ir_030&quot;: &quot;blocked&quot;,
    &quot;ir_031&quot;: &quot;blocked&quot;,
    &quot;ir_032&quot;: &quot;blocked&quot;,
    &quot;ir_033&quot;: &quot;blocked&quot;,
    &quot;ir_034&quot;: &quot;blocked&quot;,
    &quot;ir_035&quot;: &quot;blocked&quot;,
    &quot;ir_036&quot;: &quot;blocked&quot;,
    &quot;ir_037&quot;: &quot;blocked&quot;,
    &quot;ir_038&quot;: &quot;blocked&quot;,
    &quot;ir_039&quot;: &quot;blocked&quot;,
    &quot;ir_040&quot;: &quot;blocked&quot;,
    &quot;ir_041&quot;: &quot;blocked&quot;,
    &quot;ir_042&quot;: &quot;blocked&quot;,
    &quot;ir_043&quot;: &quot;blocked&quot;,
    &quot;ir_044&quot;: &quot;blocked&quot;,
    &quot;ir_045&quot;: &quot;blocked&quot;,
    &quot;ir_046&quot;: &quot;blocked&quot;,
    &quot;ir_047&quot;: &quot;blocked&quot;,
    &quot;ir_048&quot;: &quot;blocked&quot;,
    &quot;ir_049&quot;: &quot;blocked&quot;,
    &quot;ir_050&quot;: &quot;blocked&quot;,
    &quot;ir_051&quot;: &quot;blocked&quot;,
    &quot;ir_052&quot;: &quot;blocked&quot;,
    &quot;ir_053&quot;: &quot;blocked&quot;,
    &quot;ir_054&quot;: &quot;blocked&quot;,
    &quot;ir_055&quot;: &quot;blocked&quot;,
    &quot;ir_056&quot;: &quot;blocked&quot;,
    &quot;ir_057&quot;: &quot;blocked&quot;,
    &quot;ir_058&quot;: &quot;blocked&quot;,
    &quot;ir_059&quot;: &quot;blocked&quot;,
    &quot;ir_060&quot;: &quot;blocked&quot;,
    &quot;ir_061&quot;: &quot;blocked&quot;,
    &quot;ir_062&quot;: &quot;blocked&quot;
  },
  &quot;diagnostics&quot;: [
    {
      &quot;code&quot;: &quot;unmodeled_processing&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;reason&quot;: &quot;Explicitly unmodeled processing stops this block before evaluation and OUT publication; prior records remain available.&quot;
    },
    {
      &quot;code&quot;: &quot;unmodeled_processing&quot;,
      &quot;instruction_id&quot;: &quot;ir_026&quot;,
      &quot;reason&quot;: &quot;Explicitly unmodeled processing stops this block before evaluation and OUT publication; prior records remain available.&quot;
    }
  ],
  &quot;processing_gaps&quot;: [
    {
      &quot;control&quot;: true,
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 18,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 6
        }
      ],
      &quot;instruction_id&quot;: &quot;ir_002&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;source&quot;,
      &quot;outputs&quot;: [],
      &quot;reason&quot;: &quot;The abstract activation selector has no supplied concrete encoding. Its Boolean placeholder preserves the CFG&#x27;s two supported activation choices without inventing a source-level test.&quot;,
      &quot;unmodeled&quot;: false,
      &quot;validation_errors&quot;: []
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 16,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 14
        }
      ],
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;source&quot;,
      &quot;outputs&quot;: [
        1,
        2
      ],
      &quot;reason&quot;: &quot;The atomic call form exposes one normal response, not separately correlated exception and completion outputs. Source-backed placeholders retain this call&#x27;s exceptional value and Boolean control. Their availability remains restricted by the original CFG&#x27;s normal and exceptional continuations.&quot;,
      &quot;unmodeled&quot;: false,
      &quot;validation_errors&quot;: []
    },
    {
      &quot;control&quot;: true,
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 16,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 15
        }
      ],
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;source&quot;,
      &quot;outputs&quot;: [
        0,
        1
      ],
      &quot;reason&quot;: &quot;Requests&#x27; internal status predicate and exception construction are absent. The local invocation effect and its outcome placeholders retain the status-check boundary; no response.json call occurs on the exceptional continuation.&quot;,
      &quot;unmodeled&quot;: false,
      &quot;validation_errors&quot;: []
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 16,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 16
        }
      ],
      &quot;instruction_id&quot;: &quot;ir_013&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;source&quot;,
      &quot;outputs&quot;: [
        1,
        2
      ],
      &quot;reason&quot;: &quot;The normal decoded version and exceptional outcome belong to this same response.json invocation. The primitive vocabulary does not jointly bind those conditional outputs, so exception and completion placeholders retain their source occurrence and CFG-restricted availability.&quot;,
      &quot;unmodeled&quot;: false,
      &quot;validation_errors&quot;: []
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 24,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 24
        }
      ],
      &quot;instruction_id&quot;: &quot;ir_032&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;source&quot;,
      &quot;outputs&quot;: [
        2,
        3
      ],
      &quot;reason&quot;: &quot;The conversion&#x27;s actual exception and normal-completion control require conditional outcome slots beyond the scalar compute result. Placeholders preserve those slots; neither successful integers nor request results supply the exception.&quot;,
      &quot;unmodeled&quot;: false,
      &quot;validation_errors&quot;: []
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 19,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 15
        },
        {
          &quot;end_line&quot;: 28,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 27
        }
      ],
      &quot;instruction_id&quot;: &quot;ir_039&quot;,
      &quot;locations&quot;: [
        &quot;api_key_environment&quot;
      ],
      &quot;origin&quot;: &quot;source&quot;,
      &quot;outputs&quot;: [],
      &quot;reason&quot;: &quot;The Skill requires credential storage in a workspace .env file, but the implementation supplies no file loader or other file-to-process-environment handoff. This read therefore has process-environment provenance only; no file read, file ownership or storage execution is inferred.&quot;,
      &quot;unmodeled&quot;: false,
      &quot;validation_errors&quot;: []
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 19,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 15
        },
        {
          &quot;end_line&quot;: 28,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 28
        }
      ],
      &quot;instruction_id&quot;: &quot;ir_041&quot;,
      &quot;locations&quot;: [
        &quot;cse_id_environment&quot;
      ],
      &quot;origin&quot;: &quot;source&quot;,
      &quot;outputs&quot;: [],
      &quot;reason&quot;: &quot;The documented .env entry and this environment lookup are not connected by an evidenced loader. The environment value remains distinct from any hypothetical stored-file version.&quot;,
      &quot;unmodeled&quot;: false,
      &quot;validation_errors&quot;: []
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 28,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 26
        },
        {
          &quot;end_line&quot;: 35,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 23
        }
      ],
      &quot;instruction_id&quot;: &quot;ir_045&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;source&quot;,
      &quot;outputs&quot;: [],
      &quot;reason&quot;: &quot;The example invokes skills/google-search/scripts/search.py, whereas the supplied implementation is skill/scripts/search.py. Their relationship is unestablished. If the command reaches this CLI, its query and credentials bind to the corresponding slots and its omitted count selects 5; execution of that handoff is not asserted.&quot;,
      &quot;unmodeled&quot;: false,
      &quot;validation_errors&quot;: []
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 14,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 14
        },
        {
          &quot;end_line&quot;: 37,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 34
        }
      ],
      &quot;instruction_id&quot;: &quot;ir_047&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;source&quot;,
      &quot;outputs&quot;: [
        1,
        2
      ],
      &quot;reason&quot;: &quot;The normal HTTP response and actual raised exception are alternative outcomes of this CLI helper request. Outcome placeholders preserve this occurrence and the CFG-restricted availability, rather than treating an exception as successful API content.&quot;,
      &quot;unmodeled&quot;: false,
      &quot;validation_errors&quot;: []
    },
    {
      &quot;control&quot;: true,
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 15,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 15
        },
        {
          &quot;end_line&quot;: 37,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 35
        }
      ],
      &quot;instruction_id&quot;: &quot;ir_049&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;source&quot;,
      &quot;outputs&quot;: [
        0,
        1
      ],
      &quot;reason&quot;: &quot;The supplied source does not expose Requests&#x27; internal status predicate or exception construction. The local effect and outcome placeholders preserve this helper invocation&#x27;s status check and its alternative continuation.&quot;,
      &quot;unmodeled&quot;: false,
      &quot;validation_errors&quot;: []
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 16,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 16
        },
        {
          &quot;end_line&quot;: 37,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 35
        }
      ],
      &quot;instruction_id&quot;: &quot;ir_051&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;source&quot;,
      &quot;outputs&quot;: [
        1,
        2
      ],
      &quot;reason&quot;: &quot;Conditional exception and completion slots are retained with local placeholders for this decoding occurrence. They do not replace, alias or originate from its successful decoded content.&quot;,
      &quot;unmodeled&quot;: false,
      &quot;validation_errors&quot;: []
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 37,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 35
        }
      ],
      &quot;instruction_id&quot;: &quot;ir_053&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;source&quot;,
      &quot;outputs&quot;: [
        2,
        3
      ],
      &quot;reason&quot;: &quot;Serialization&#x27;s conditional exception and completion slots are represented by source-backed placeholders. A serialization failure preserves the already received decoded results binding and supplies no successful formatted string.&quot;,
      &quot;unmodeled&quot;: false,
      &quot;validation_errors&quot;: []
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 38,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 36
        }
      ],
      &quot;instruction_id&quot;: &quot;ir_055&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;source&quot;,
      &quot;outputs&quot;: [
        0,
        1
      ],
      &quot;reason&quot;: &quot;Print may raise after partial delivery. Outcome placeholders retain the actual print exception and normal-completion control; the supplied source establishes neither an exact delivered prefix nor rollback.&quot;,
      &quot;unmodeled&quot;: false,
      &quot;validation_errors&quot;: []
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 28,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 21
        },
        {
          &quot;end_line&quot;: 39,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 6
        }
      ],
      &quot;instruction_id&quot;: &quot;ir_057&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;source&quot;,
      &quot;outputs&quot;: [],
      &quot;reason&quot;: &quot;The Workflow is a placeholder. No per-element traversal, yield collection, save, later file read, retry, summarization or application-level shared-state update is supplied. No saved-result provenance or downstream model routing can be attached to this completion.&quot;,
      &quot;unmodeled&quot;: false,
      &quot;validation_errors&quot;: []
    },
    {
      &quot;control&quot;: true,
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 39,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 37
        }
      ],
      &quot;instruction_id&quot;: &quot;ir_061&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;source&quot;,
      &quot;outputs&quot;: [],
      &quot;reason&quot;: &quot;Error conversion and printing may themselves fail outside the protected try body. Their concrete exceptional payloads are not CFG outputs here; sys.exit(1) is reached only after those handler actions complete normally.&quot;,
      &quot;unmodeled&quot;: false,
      &quot;validation_errors&quot;: []
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_061&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;validation&quot;,
      &quot;outputs&quot;: [],
      &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
      &quot;unmodeled&quot;: true,
      &quot;validation_errors&quot;: [
        {
          &quot;code&quot;: &quot;source_action_role&quot;,
          &quot;message&quot;: &quot;Source action &#x27;str_e&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
          &quot;path&quot;: &quot;/ir_semantics/ir_061/action_bindings&quot;
        },
        {
          &quot;code&quot;: &quot;source_action_role&quot;,
          &quot;message&quot;: &quot;Source action &#x27;error_sys_exit&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
          &quot;path&quot;: &quot;/ir_semantics/ir_061/action_bindings&quot;
        }
      ]
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_053&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;validation&quot;,
      &quot;outputs&quot;: [],
      &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
      &quot;unmodeled&quot;: true,
      &quot;validation_errors&quot;: [
        {
          &quot;code&quot;: &quot;source_action_role&quot;,
          &quot;message&quot;: &quot;Source action &#x27;json_dumps&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
          &quot;path&quot;: &quot;/ir_semantics/ir_053/action_bindings&quot;
        }
      ]
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_051&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;validation&quot;,
      &quot;outputs&quot;: [],
      &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
      &quot;unmodeled&quot;: true,
      &quot;validation_errors&quot;: [
        {
          &quot;code&quot;: &quot;source_action_role&quot;,
          &quot;message&quot;: &quot;Source action &#x27;cli.response_json&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
          &quot;path&quot;: &quot;/ir_semantics/ir_051/action_bindings&quot;
        }
      ]
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_049&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;validation&quot;,
      &quot;outputs&quot;: [],
      &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
      &quot;unmodeled&quot;: true,
      &quot;validation_errors&quot;: [
        {
          &quot;code&quot;: &quot;source_action_role&quot;,
          &quot;message&quot;: &quot;Source action &#x27;cli.raise_for_status&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
          &quot;path&quot;: &quot;/ir_semantics/ir_049/action_bindings&quot;
        }
      ]
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_045&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;validation&quot;,
      &quot;outputs&quot;: [],
      &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
      &quot;unmodeled&quot;: true,
      &quot;validation_errors&quot;: [
        {
          &quot;code&quot;: &quot;source_action_role&quot;,
          &quot;message&quot;: &quot;Source action &#x27;google_search_call&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
          &quot;path&quot;: &quot;/ir_semantics/ir_045/action_bindings&quot;
        }
      ]
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_043&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;validation&quot;,
      &quot;outputs&quot;: [],
      &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
      &quot;unmodeled&quot;: true,
      &quot;validation_errors&quot;: [
        {
          &quot;code&quot;: &quot;source_action_role&quot;,
          &quot;message&quot;: &quot;Source action &#x27;credential_sys_exit&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
          &quot;path&quot;: &quot;/ir_semantics/ir_043/action_bindings&quot;
        }
      ]
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_032&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;validation&quot;,
      &quot;outputs&quot;: [],
      &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
      &quot;unmodeled&quot;: true,
      &quot;validation_errors&quot;: [
        {
          &quot;code&quot;: &quot;source_action_role&quot;,
          &quot;message&quot;: &quot;Source action &#x27;int_count&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
          &quot;path&quot;: &quot;/ir_semantics/ir_032/action_bindings&quot;
        }
      ]
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_028&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;validation&quot;,
      &quot;outputs&quot;: [],
      &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
      &quot;unmodeled&quot;: true,
      &quot;validation_errors&quot;: [
        {
          &quot;code&quot;: &quot;source_action_role&quot;,
          &quot;message&quot;: &quot;Source action &#x27;usage_sys_exit&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
          &quot;path&quot;: &quot;/ir_semantics/ir_028/action_bindings&quot;
        }
      ]
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_026&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;validation&quot;,
      &quot;outputs&quot;: [],
      &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
      &quot;unmodeled&quot;: true,
      &quot;validation_errors&quot;: [
        {
          &quot;code&quot;: &quot;source_action_role&quot;,
          &quot;message&quot;: &quot;Source action &#x27;cli.argv_length&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
          &quot;path&quot;: &quot;/ir_semantics/ir_026/action_bindings&quot;
        }
      ]
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_013&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;validation&quot;,
      &quot;outputs&quot;: [],
      &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
      &quot;unmodeled&quot;: true,
      &quot;validation_errors&quot;: [
        {
          &quot;code&quot;: &quot;source_action_role&quot;,
          &quot;message&quot;: &quot;Source action &#x27;public.response_json&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
          &quot;path&quot;: &quot;/ir_semantics/ir_013/action_bindings&quot;
        }
      ]
    },
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;locations&quot;: [],
      &quot;origin&quot;: &quot;validation&quot;,
      &quot;outputs&quot;: [],
      &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
      &quot;unmodeled&quot;: true,
      &quot;validation_errors&quot;: [
        {
          &quot;code&quot;: &quot;source_action_role&quot;,
          &quot;message&quot;: &quot;Source action &#x27;public.raise_for_status&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
          &quot;path&quot;: &quot;/ir_semantics/ir_010/action_bindings&quot;
        }
      ]
    }
  ]
}</pre>

</details>

## ir_001 · receive

Block: block_001; Operator: unknown.

IR inputs: 0: analysis.activation_kind

IR outputs: 0: result_001

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Retained binding and explicit write changes: 

- `result: result_001`: Unbound → D022

<details><summary>Retained entry and exit evidence</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_a66a605573710f6a1c206756c81c9eab853d00915b3b4e117482ab9542e2c4bc&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;analysis.activation_kind&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;direct_execution.sys.argv&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.api_key&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.cse_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_03788283a4a95be43be23e33579fedfad245022778073d07cfd54cadbd7b91d2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.num_results&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.query&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3aabd5921a1f574dba69160be63eb434bb3ccf93bf56414a439ed10f9853f51f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;module_evaluation.__name__&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_a66a605573710f6a1c206756c81c9eab853d00915b3b4e117482ab9542e2c4bc&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;direct_execution.sys.argv&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.api_key&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.cse_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_03788283a4a95be43be23e33579fedfad245022778073d07cfd54cadbd7b91d2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.num_results&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.query&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3aabd5921a1f574dba69160be63eb434bb3ccf93bf56414a439ed10f9853f51f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;module_evaluation.__name__&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;reason&quot;: &quot;Acquire the activation selector independently of invocation arguments.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_001&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      }
    ],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;reason&quot;: &quot;Acquire the activation selector independently of invocation arguments.&quot;,
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_001&quot;,
            &quot;path&quot;: []
          }
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      }
    }
  ],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_002 · dispatch

Block: block_001; Operator: unknown.

IR inputs: 0: result_001

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    }
  ]
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | Unlabeled data operation | placeholder | 0: D022 | — | 0: D028 |
| 2.1 | Unlabeled data operation | branch | 0: D028 | — | — |

Retained binding and explicit write changes: 

- No retained binding change is shown; this does not imply absence of observation, sending or omitted historical bindings.

<details><summary>Retained entry and exit evidence</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_a66a605573710f6a1c206756c81c9eab853d00915b3b4e117482ab9542e2c4bc&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;direct_execution.sys.argv&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.api_key&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.cse_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_03788283a4a95be43be23e33579fedfad245022778073d07cfd54cadbd7b91d2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.num_results&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.query&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3aabd5921a1f574dba69160be63eb434bb3ccf93bf56414a439ed10f9853f51f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;module_evaluation.__name__&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;direct_execution.sys.argv&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.api_key&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.cse_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_03788283a4a95be43be23e33579fedfad245022778073d07cfd54cadbd7b91d2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.num_results&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.query&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3aabd5921a1f574dba69160be63eb434bb3ccf93bf56414a439ed10f9853f51f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;module_evaluation.__name__&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 18,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 6
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 0,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;kind&quot;: &quot;value&quot;,
            &quot;op&quot;: &quot;placeholder&quot;,
            &quot;output&quot;: &quot;public_activation&quot;,
            &quot;reason&quot;: &quot;The CFG supplies the activation alternatives but leaves the selector&#x27;s concrete representation unspecified.&quot;
          }
        ],
        &quot;effect&quot;: null
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;reason&quot;: &quot;The CFG distinguishes public invocation from module evaluation; it does not specify a concrete selector encoding.&quot;,
                &quot;target&quot;: {
                  &quot;instruction_id&quot;: &quot;ir_002&quot;,
                  &quot;path&quot;: []
                }
              }
            ],
            &quot;false_target&quot;: &quot;block_011&quot;,
            &quot;input&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;public_activation&quot;
            },
            &quot;op&quot;: &quot;branch&quot;,
            &quot;predicate&quot;: &quot;truthy&quot;,
            &quot;true_target&quot;: &quot;block_002&quot;
          }
        ],
        &quot;effect&quot;: null
      }
    ],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 0
        }
      }
    ],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 18,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 6
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;kind&quot;: &quot;value&quot;,
      &quot;op&quot;: &quot;placeholder&quot;,
      &quot;output&quot;: &quot;public_activation&quot;,
      &quot;reason&quot;: &quot;The CFG supplies the activation alternatives but leaves the selector&#x27;s concrete representation unspecified.&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;reason&quot;: &quot;The CFG distinguishes public invocation from module evaluation; it does not specify a concrete selector encoding.&quot;,
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_002&quot;,
            &quot;path&quot;: []
          }
        }
      ],
      &quot;false_target&quot;: &quot;block_011&quot;,
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;public_activation&quot;
      },
      &quot;op&quot;: &quot;branch&quot;,
      &quot;predicate&quot;: &quot;truthy&quot;,
      &quot;true_target&quot;: &quot;block_002&quot;
    }
  ]
}</pre>

</details>

## ir_003 · receive

Block: block_002; Operator: unknown.

IR inputs: 0: google_search.invocation.bound.query, 1: google_search.invocation.bound.api_key, 2: google_search.invocation.bound.cse_id, 3: google_search.invocation.bound.num_results

IR outputs: 0: result_002, 1: result_003, 2: result_004, 3: result_005

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Retained binding and explicit write changes: 

- `result: result_002`: Unbound → D024
- `result: result_003`: Unbound → D025
- `result: result_004`: Unbound → D023
- `result: result_005`: Unbound → D004, D007

<details><summary>Retained entry and exit evidence</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.api_key&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.cse_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_03788283a4a95be43be23e33579fedfad245022778073d07cfd54cadbd7b91d2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.num_results&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;google_search.invocation.bound.query&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1c0589d90480a256bda88a1a911db646a2eb65fdf672d470adedfd78785bb417&quot;,
          &quot;data_2f0ee426a970315ff5348642d81538c8ddc677f5045ea4d1840da5a9d73c6c77&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 6,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Bind each parameter to its own invocation input snapshot, preserving the optional count snapshot and the source-supported default 5 without replacing the entry snapshot with a computed default.&quot;,
            &quot;start_line&quot;: 6
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      },
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 6,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Bind each parameter to its own invocation input snapshot, preserving the optional count snapshot and the source-supported default 5 without replacing the entry snapshot with a computed default.&quot;,
            &quot;start_line&quot;: 6
          }
        ],
        &quot;output_index&quot;: 1,
        &quot;value&quot;: {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        }
      },
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 6,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Bind each parameter to its own invocation input snapshot, preserving the optional count snapshot and the source-supported default 5 without replacing the entry snapshot with a computed default.&quot;,
            &quot;start_line&quot;: 6
          }
        ],
        &quot;output_index&quot;: 2,
        &quot;value&quot;: {
          &quot;index&quot;: 2,
          &quot;kind&quot;: &quot;input&quot;
        }
      },
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 6,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Bind each parameter to its own invocation input snapshot, preserving the optional count snapshot and the source-supported default 5 without replacing the entry snapshot with a computed default.&quot;,
            &quot;start_line&quot;: 6
          }
        ],
        &quot;output_index&quot;: 3,
        &quot;value&quot;: {
          &quot;index&quot;: 3,
          &quot;kind&quot;: &quot;input&quot;
        }
      }
    ],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 19,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The Skill identifies the API key as a credential, supporting sensitivity of the entire credential field independently of its accesses.&quot;,
            &quot;start_line&quot;: 13
          },
          {
            &quot;end_line&quot;: 11,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;This invocation&#x27;s api_key parameter supplies the request&#x27;s key field; the declaration covers the original bound argument.&quot;,
            &quot;start_line&quot;: 6
          }
        ],
        &quot;label&quot;: &quot;API credential&quot;,
        &quot;path&quot;: [],
        &quot;property&quot;: &quot;value&quot;,
        &quot;source_access_id&quot;: &quot;access_a8a5938bc41ef8de647e7f3e&quot;,
        &quot;source_entry_applicability&quot;: &quot;source_field&quot;,
        &quot;source_entry_context&quot;: &quot;872bf9fd17c7a9c3fd3d359543a8a3564094ab68bdc8c622405bae727c9f0215&quot;,
        &quot;source_entry_id&quot;: &quot;entry_a99bc97f8d1f4a9dc277bff1&quot;,
        &quot;source_entry_location&quot;: &quot;runtime_context:google_search.invocation.bound.api_key&quot;,
        &quot;source_entry_origin&quot;: &quot;skill_argument&quot;,
        &quot;value&quot;: {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        }
      },
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 19,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The Skill includes the CX ID among credentials, supporting sensitivity of the entire credential field independently of its accesses.&quot;,
            &quot;start_line&quot;: 14
          },
          {
            &quot;end_line&quot;: 11,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;This invocation&#x27;s cse_id parameter supplies the request&#x27;s cx field; the declaration covers the original bound argument.&quot;,
            &quot;start_line&quot;: 6
          }
        ],
        &quot;label&quot;: &quot;Search engine credential&quot;,
        &quot;path&quot;: [],
        &quot;property&quot;: &quot;value&quot;,
        &quot;source_access_id&quot;: &quot;access_2e977d982b523d2290dfea2c&quot;,
        &quot;source_entry_applicability&quot;: &quot;source_field&quot;,
        &quot;source_entry_context&quot;: &quot;872bf9fd17c7a9c3fd3d359543a8a3564094ab68bdc8c622405bae727c9f0215&quot;,
        &quot;source_entry_id&quot;: &quot;entry_25133a4ea1320fa498ba81cf&quot;,
        &quot;source_entry_location&quot;: &quot;runtime_context:google_search.invocation.bound.cse_id&quot;,
        &quot;source_entry_origin&quot;: &quot;skill_argument&quot;,
        &quot;value&quot;: {
          &quot;index&quot;: 2,
          &quot;kind&quot;: &quot;input&quot;
        }
      }
    ]
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 6,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Bind each parameter to its own invocation input snapshot, preserving the optional count snapshot and the source-supported default 5 without replacing the entry snapshot with a computed default.&quot;,
          &quot;start_line&quot;: 6
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 6,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Bind each parameter to its own invocation input snapshot, preserving the optional count snapshot and the source-supported default 5 without replacing the entry snapshot with a computed default.&quot;,
          &quot;start_line&quot;: 6
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 6,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Bind each parameter to its own invocation input snapshot, preserving the optional count snapshot and the source-supported default 5 without replacing the entry snapshot with a computed default.&quot;,
          &quot;start_line&quot;: 6
        }
      ],
      &quot;output_index&quot;: 2,
      &quot;value&quot;: {
        &quot;index&quot;: 2,
        &quot;kind&quot;: &quot;input&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 6,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Bind each parameter to its own invocation input snapshot, preserving the optional count snapshot and the source-supported default 5 without replacing the entry snapshot with a computed default.&quot;,
          &quot;start_line&quot;: 6
        }
      ],
      &quot;output_index&quot;: 3,
      &quot;value&quot;: {
        &quot;index&quot;: 3,
        &quot;kind&quot;: &quot;input&quot;
      }
    }
  ],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_004 · dispatch

Block: block_002; Operator: unknown.

IR inputs: []

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Retained binding and explicit write changes: 

- No retained binding change is shown; this does not imply absence of observation, sending or omitted historical bindings.

<details><summary>Retained entry and exit evidence</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1c0589d90480a256bda88a1a911db646a2eb65fdf672d470adedfd78785bb417&quot;,
          &quot;data_2f0ee426a970315ff5348642d81538c8ddc677f5045ea4d1840da5a9d73c6c77&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1c0589d90480a256bda88a1a911db646a2eb65fdf672d470adedfd78785bb417&quot;,
          &quot;data_2f0ee426a970315ff5348642d81538c8ddc677f5045ea4d1840da5a9d73c6c77&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_005 · value

Block: block_003; Operator: unknown.

IR inputs: 0: &quot;https://www.googleapis.com/customsearch/v1&quot;, 1: result_002, 2: result_003, 3: result_004, 4: result_005

IR outputs: 0: result_006, 1: result_007

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | transform | build | 0: D024; 1: D025; 2: D023; 3: D004, D007 | — | 0: D013, D026 |
| 1.1 · Member | — | [   &quot;q&quot; ] | Original-value slot 0; Condition slot None | — | Include original value |
| 1.1 · Member | — | [   &quot;key&quot; ] | Original-value slot 1; Condition slot None | — | Include original value |
| 1.1 · Member | — | [   &quot;cx&quot; ] | Original-value slot 2; Condition slot None | — | Include original value |
| 1.1 · Member | — | [   &quot;num&quot; ] | Original-value slot 3; Condition slot None | — | Include original value |

Retained binding and explicit write changes: 

- `result: result_006`: Unbound → D027
- `result: result_007`: Unbound → D013, D026

<details><summary>Retained entry and exit evidence</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1c0589d90480a256bda88a1a911db646a2eb65fdf672d470adedfd78785bb417&quot;,
          &quot;data_2f0ee426a970315ff5348642d81538c8ddc677f5045ea4d1840da5a9d73c6c77&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_cc5a1213aa56ef408a4aeecf69bc1f0f8904698f3d580b404c8423831523ad7c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_689fc477090c720437e9cab8439dda52e583e47500738ed1b7ce681bae70b8bf&quot;,
          &quot;data_c54d71e7c232dcabd654cf4946eb941468b453170f70a1c2fc8df526c6303700&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;container&quot;: &quot;object&quot;,
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 13,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 7
              }
            ],
            &quot;op&quot;: &quot;build&quot;,
            &quot;output&quot;: &quot;params&quot;,
            &quot;parts&quot;: [
              {
                &quot;path&quot;: [
                  &quot;q&quot;
                ],
                &quot;value&quot;: {
                  &quot;index&quot;: 1,
                  &quot;kind&quot;: &quot;input&quot;
                },
                &quot;when&quot;: null
              },
              {
                &quot;path&quot;: [
                  &quot;key&quot;
                ],
                &quot;value&quot;: {
                  &quot;index&quot;: 2,
                  &quot;kind&quot;: &quot;input&quot;
                },
                &quot;when&quot;: null
              },
              {
                &quot;path&quot;: [
                  &quot;cx&quot;
                ],
                &quot;value&quot;: {
                  &quot;index&quot;: 3,
                  &quot;kind&quot;: &quot;input&quot;
                },
                &quot;when&quot;: null
              },
              {
                &quot;path&quot;: [
                  &quot;num&quot;
                ],
                &quot;value&quot;: {
                  &quot;index&quot;: 4,
                  &quot;kind&quot;: &quot;input&quot;
                },
                &quot;when&quot;: null
              }
            ]
          }
        ],
        &quot;effect&quot;: &quot;transform&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 13,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 7
          }
        ]
      }
    ],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 13,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 7
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      },
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 13,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 7
          }
        ],
        &quot;output_index&quot;: 1,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;params&quot;
        }
      }
    ],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 13,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 7
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 13,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 7
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;params&quot;
      }
    }
  ],
  &quot;steps&quot;: [
    {
      &quot;container&quot;: &quot;object&quot;,
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 13,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 7
        }
      ],
      &quot;op&quot;: &quot;build&quot;,
      &quot;output&quot;: &quot;params&quot;,
      &quot;parts&quot;: [
        {
          &quot;path&quot;: [
            &quot;q&quot;
          ],
          &quot;value&quot;: {
            &quot;index&quot;: 1,
            &quot;kind&quot;: &quot;input&quot;
          },
          &quot;when&quot;: null
        },
        {
          &quot;path&quot;: [
            &quot;key&quot;
          ],
          &quot;value&quot;: {
            &quot;index&quot;: 2,
            &quot;kind&quot;: &quot;input&quot;
          },
          &quot;when&quot;: null
        },
        {
          &quot;path&quot;: [
            &quot;cx&quot;
          ],
          &quot;value&quot;: {
            &quot;index&quot;: 3,
            &quot;kind&quot;: &quot;input&quot;
          },
          &quot;when&quot;: null
        },
        {
          &quot;path&quot;: [
            &quot;num&quot;
          ],
          &quot;value&quot;: {
            &quot;index&quot;: 4,
            &quot;kind&quot;: &quot;input&quot;
          },
          &quot;when&quot;: null
        }
      ]
    }
  ]
}</pre>

</details>

## ir_006 · dispatch

Block: block_003; Operator: unknown.

IR inputs: []

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Retained binding and explicit write changes: 

- No retained binding change is shown; this does not imply absence of observation, sending or omitted historical bindings.

<details><summary>Retained entry and exit evidence</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_cc5a1213aa56ef408a4aeecf69bc1f0f8904698f3d580b404c8423831523ad7c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_689fc477090c720437e9cab8439dda52e583e47500738ed1b7ce681bae70b8bf&quot;,
          &quot;data_c54d71e7c232dcabd654cf4946eb941468b453170f70a1c2fc8df526c6303700&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_cc5a1213aa56ef408a4aeecf69bc1f0f8904698f3d580b404c8423831523ad7c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_689fc477090c720437e9cab8439dda52e583e47500738ed1b7ce681bae70b8bf&quot;,
          &quot;data_c54d71e7c232dcabd654cf4946eb941468b453170f70a1c2fc8df526c6303700&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_007 · call

Block: block_004; Operator: unknown.

IR inputs: 0: requests module binding imported at skill/scripts/search.py:3, 1: result_006, 2: result_007

IR outputs: 0: result_008, 1: result_009, 2: result_010

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 2,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 3,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 2,
        &quot;op_index&quot;: 0
      }
    }
  ]
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | net_send | deliver | 0: D027; 1: D013, D026 | remote: https://www.googleapis.com/customsearch/v1 | — |
| 2.1 | net_receive | receive | 0: D027; 1: D013, D026 | remote: https://www.googleapis.com/customsearch/v1 | 0: D005, D021 |
| 3.1 | Unlabeled data operation | placeholder | — | — | 0: D003 |
| 4.1 | Unlabeled data operation | placeholder | — | — | 0: D018 |

Retained binding and explicit write changes: 

- `result: result_008`: Unbound → D005, D021
- `result: result_009`: Unbound → D003
- `result: result_010`: Unbound → D018

<details><summary>Retained entry and exit evidence</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_cc5a1213aa56ef408a4aeecf69bc1f0f8904698f3d580b404c8423831523ad7c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_689fc477090c720437e9cab8439dda52e583e47500738ed1b7ce681bae70b8bf&quot;,
          &quot;data_c54d71e7c232dcabd654cf4946eb941468b453170f70a1c2fc8df526c6303700&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_220322fdf0ccf9c13756eceff32901373e751fcf1ee834315676c8dfca69304c&quot;,
          &quot;data_9c233401d315759e046d494b00809f040bbcdac236e7cb45dea59a496056600f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_137764b44213725de1784df71500123b046868f4761a48e30333bb3194c0e793&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8e6fad11c9faa98817e73a5a1a84ebf2e928314e1a52ca6cc7e6f8c5be2220ea&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 14
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 1,
                &quot;kind&quot;: &quot;input&quot;
              },
              {
                &quot;index&quot;: 2,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;op&quot;: &quot;deliver&quot;,
            &quot;request_id&quot;: &quot;f8b04abd14a0db74a6723fa4b031c7d2601059222fe218a618a2dd1f519d98f6&quot;,
            &quot;target&quot;: &quot;google_search_api&quot;
          }
        ],
        &quot;effect&quot;: &quot;net_send&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 14,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 14
          }
        ]
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 14
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 1,
                &quot;kind&quot;: &quot;input&quot;
              },
              {
                &quot;index&quot;: 2,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;location&quot;: &quot;google_search_api&quot;,
            &quot;op&quot;: &quot;receive&quot;,
            &quot;output&quot;: &quot;response&quot;,
            &quot;request_id&quot;: &quot;f8b04abd14a0db74a6723fa4b031c7d2601059222fe218a618a2dd1f519d98f6&quot;
          }
        ],
        &quot;effect&quot;: &quot;net_receive&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 14,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 14
          }
        ]
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 14
              }
            ],
            &quot;inputs&quot;: [],
            &quot;kind&quot;: &quot;value&quot;,
            &quot;op&quot;: &quot;placeholder&quot;,
            &quot;output&quot;: &quot;exception&quot;,
            &quot;reason&quot;: &quot;The actual exception raised by this requests.get occurrence is available only on its exceptional continuation. No successful response is supplied there.&quot;
          }
        ],
        &quot;effect&quot;: null
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 14
              }
            ],
            &quot;inputs&quot;: [],
            &quot;kind&quot;: &quot;value&quot;,
            &quot;op&quot;: &quot;placeholder&quot;,
            &quot;output&quot;: &quot;returned&quot;,
            &quot;reason&quot;: &quot;Boolean normal-completion control for this request occurrence, not an additional Requests return value.&quot;
          }
        ],
        &quot;effect&quot;: null
      }
    ],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 14,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 14
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;response&quot;
        }
      },
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 14,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 14
          }
        ],
        &quot;output_index&quot;: 1,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;exception&quot;
        }
      },
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 14,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 14
          }
        ],
        &quot;output_index&quot;: 2,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;returned&quot;
        }
      }
    ],
    &quot;precedence&quot;: [
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 2,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 3,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 2,
          &quot;op_index&quot;: 0
        }
      }
    ],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 14,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 14
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;response&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 14,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 14
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;exception&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 14,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 14
        }
      ],
      &quot;output_index&quot;: 2,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;returned&quot;
      }
    }
  ],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 14,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 14
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        },
        {
          &quot;index&quot;: 2,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;request_id&quot;: &quot;f8b04abd14a0db74a6723fa4b031c7d2601059222fe218a618a2dd1f519d98f6&quot;,
      &quot;target&quot;: &quot;google_search_api&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 14,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 14
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        },
        {
          &quot;index&quot;: 2,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;location&quot;: &quot;google_search_api&quot;,
      &quot;op&quot;: &quot;receive&quot;,
      &quot;output&quot;: &quot;response&quot;,
      &quot;request_id&quot;: &quot;f8b04abd14a0db74a6723fa4b031c7d2601059222fe218a618a2dd1f519d98f6&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 14,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 14
        }
      ],
      &quot;inputs&quot;: [],
      &quot;kind&quot;: &quot;value&quot;,
      &quot;op&quot;: &quot;placeholder&quot;,
      &quot;output&quot;: &quot;exception&quot;,
      &quot;reason&quot;: &quot;The actual exception raised by this requests.get occurrence is available only on its exceptional continuation. No successful response is supplied there.&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 14,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 14
        }
      ],
      &quot;inputs&quot;: [],
      &quot;kind&quot;: &quot;value&quot;,
      &quot;op&quot;: &quot;placeholder&quot;,
      &quot;output&quot;: &quot;returned&quot;,
      &quot;reason&quot;: &quot;Boolean normal-completion control for this request occurrence, not an additional Requests return value.&quot;
    }
  ]
}</pre>

</details>

## ir_008 · dispatch

Block: block_004; Operator: unknown.

IR inputs: 0: result_010

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | Unlabeled data operation | branch | 0: D018 | — | — |

Retained binding and explicit write changes: 

- No retained binding change is shown; this does not imply absence of observation, sending or omitted historical bindings.

<details><summary>Retained entry and exit evidence</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_220322fdf0ccf9c13756eceff32901373e751fcf1ee834315676c8dfca69304c&quot;,
          &quot;data_9c233401d315759e046d494b00809f040bbcdac236e7cb45dea59a496056600f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_137764b44213725de1784df71500123b046868f4761a48e30333bb3194c0e793&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8e6fad11c9faa98817e73a5a1a84ebf2e928314e1a52ca6cc7e6f8c5be2220ea&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_220322fdf0ccf9c13756eceff32901373e751fcf1ee834315676c8dfca69304c&quot;,
          &quot;data_9c233401d315759e046d494b00809f040bbcdac236e7cb45dea59a496056600f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_137764b44213725de1784df71500123b046868f4761a48e30333bb3194c0e793&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8e6fad11c9faa98817e73a5a1a84ebf2e928314e1a52ca6cc7e6f8c5be2220ea&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 14
              }
            ],
            &quot;false_target&quot;: &quot;block_005&quot;,
            &quot;input&quot;: {
              &quot;index&quot;: 0,
              &quot;kind&quot;: &quot;input&quot;
            },
            &quot;op&quot;: &quot;branch&quot;,
            &quot;predicate&quot;: &quot;truthy&quot;,
            &quot;true_target&quot;: &quot;block_006&quot;
          }
        ],
        &quot;effect&quot;: null
      }
    ],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 14,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 14
        }
      ],
      &quot;false_target&quot;: &quot;block_005&quot;,
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;branch&quot;,
      &quot;predicate&quot;: &quot;truthy&quot;,
      &quot;true_target&quot;: &quot;block_006&quot;
    }
  ]
}</pre>

</details>

## ir_009 · return

Block: block_005; Operator: unknown.

IR inputs: 0: result_009

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Retained binding and explicit write changes: 

- No retained binding change is shown; this does not imply absence of observation, sending or omitted historical bindings.

<details><summary>Retained entry and exit evidence</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_137764b44213725de1784df71500123b046868f4761a48e30333bb3194c0e793&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: []
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_017 · initialize_import_bindings

Block: block_011; Operator: unknown.

IR inputs: 0: Python import machinery

IR outputs: 0: result_016, 1: result_017, 2: result_018, 3: result_019

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 2,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 3,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 2,
        &quot;op_index&quot;: 0
      }
    }
  ]
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | Unlabeled data operation | placeholder | — | — | 0: D019 |
| 2.1 | Unlabeled data operation | placeholder | — | — | 0: D020 |
| 3.1 | Unlabeled data operation | placeholder | — | — | 0: D011 |
| 4.1 | Unlabeled data operation | placeholder | — | — | 0: D012 |

Retained binding and explicit write changes: 

- `result: result_016`: Unbound → D019
- `result: result_017`: Unbound → D020
- `result: result_018`: Unbound → D011
- `result: result_019`: Unbound → D012

<details><summary>Retained entry and exit evidence</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;direct_execution.sys.argv&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3aabd5921a1f574dba69160be63eb434bb3ccf93bf56414a439ed10f9853f51f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;module_evaluation.__name__&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_8e844e5cb282c55c895e724b05e6451a5fced57a1593a04f23d6899b8c5a42cf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_016&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_92df6ad582519f16573ebfc5af0dc7c28be2c0e2100b6799687f7b5f28ee9d82&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_017&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_49ceaf15d81094a0550fab7fdbf658a5897368ea823a969e2744dd825f6e7bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_018&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_685aea391daa2182e78b4a260cff0cda06a48d1701bdb8857001d2779bcd64c4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_019&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;direct_execution.sys.argv&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3aabd5921a1f574dba69160be63eb434bb3ccf93bf56414a439ed10f9853f51f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;module_evaluation.__name__&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 1,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 1
              }
            ],
            &quot;inputs&quot;: [],
            &quot;kind&quot;: &quot;value&quot;,
            &quot;op&quot;: &quot;placeholder&quot;,
            &quot;output&quot;: &quot;sys_module&quot;,
            &quot;reason&quot;: &quot;The import initializes the sys binding; module creation versus reuse is unspecified.&quot;
          }
        ],
        &quot;effect&quot;: null
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 2,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 2
              }
            ],
            &quot;inputs&quot;: [],
            &quot;kind&quot;: &quot;value&quot;,
            &quot;op&quot;: &quot;placeholder&quot;,
            &quot;output&quot;: &quot;json_module&quot;,
            &quot;reason&quot;: &quot;The import initializes the json binding; module creation versus reuse is unspecified.&quot;
          }
        ],
        &quot;effect&quot;: null
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 3,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 3
              }
            ],
            &quot;inputs&quot;: [],
            &quot;kind&quot;: &quot;value&quot;,
            &quot;op&quot;: &quot;placeholder&quot;,
            &quot;output&quot;: &quot;requests_module&quot;,
            &quot;reason&quot;: &quot;The import initializes the requests binding; module creation versus reuse is unspecified.&quot;
          }
        ],
        &quot;effect&quot;: null
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 4,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 4
              }
            ],
            &quot;inputs&quot;: [],
            &quot;kind&quot;: &quot;value&quot;,
            &quot;op&quot;: &quot;placeholder&quot;,
            &quot;output&quot;: &quot;os_module&quot;,
            &quot;reason&quot;: &quot;The import initializes the os binding; module creation versus reuse is unspecified.&quot;
          }
        ],
        &quot;effect&quot;: null
      }
    ],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 4,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 1
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;sys_module&quot;
        }
      },
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 4,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 1
          }
        ],
        &quot;output_index&quot;: 1,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;json_module&quot;
        }
      },
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 4,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 1
          }
        ],
        &quot;output_index&quot;: 2,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;requests_module&quot;
        }
      },
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 4,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 1
          }
        ],
        &quot;output_index&quot;: 3,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;os_module&quot;
        }
      }
    ],
    &quot;precedence&quot;: [
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 2,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 3,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 2,
          &quot;op_index&quot;: 0
        }
      }
    ],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 4,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 1
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;sys_module&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 4,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 1
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;json_module&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 4,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 1
        }
      ],
      &quot;output_index&quot;: 2,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;requests_module&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 4,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 1
        }
      ],
      &quot;output_index&quot;: 3,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;os_module&quot;
      }
    }
  ],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 1,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 1
        }
      ],
      &quot;inputs&quot;: [],
      &quot;kind&quot;: &quot;value&quot;,
      &quot;op&quot;: &quot;placeholder&quot;,
      &quot;output&quot;: &quot;sys_module&quot;,
      &quot;reason&quot;: &quot;The import initializes the sys binding; module creation versus reuse is unspecified.&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 2,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 2
        }
      ],
      &quot;inputs&quot;: [],
      &quot;kind&quot;: &quot;value&quot;,
      &quot;op&quot;: &quot;placeholder&quot;,
      &quot;output&quot;: &quot;json_module&quot;,
      &quot;reason&quot;: &quot;The import initializes the json binding; module creation versus reuse is unspecified.&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 3,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 3
        }
      ],
      &quot;inputs&quot;: [],
      &quot;kind&quot;: &quot;value&quot;,
      &quot;op&quot;: &quot;placeholder&quot;,
      &quot;output&quot;: &quot;requests_module&quot;,
      &quot;reason&quot;: &quot;The import initializes the requests binding; module creation versus reuse is unspecified.&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 4,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 4
        }
      ],
      &quot;inputs&quot;: [],
      &quot;kind&quot;: &quot;value&quot;,
      &quot;op&quot;: &quot;placeholder&quot;,
      &quot;output&quot;: &quot;os_module&quot;,
      &quot;reason&quot;: &quot;The import initializes the os binding; module creation versus reuse is unspecified.&quot;
    }
  ]
}</pre>

</details>

## ir_018 · dispatch

Block: block_011; Operator: unknown.

IR inputs: []

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Retained binding and explicit write changes: 

- No retained binding change is shown; this does not imply absence of observation, sending or omitted historical bindings.

<details><summary>Retained entry and exit evidence</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_8e844e5cb282c55c895e724b05e6451a5fced57a1593a04f23d6899b8c5a42cf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_016&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_92df6ad582519f16573ebfc5af0dc7c28be2c0e2100b6799687f7b5f28ee9d82&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_017&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_49ceaf15d81094a0550fab7fdbf658a5897368ea823a969e2744dd825f6e7bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_018&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_685aea391daa2182e78b4a260cff0cda06a48d1701bdb8857001d2779bcd64c4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_019&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;direct_execution.sys.argv&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3aabd5921a1f574dba69160be63eb434bb3ccf93bf56414a439ed10f9853f51f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;module_evaluation.__name__&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_8e844e5cb282c55c895e724b05e6451a5fced57a1593a04f23d6899b8c5a42cf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_016&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_92df6ad582519f16573ebfc5af0dc7c28be2c0e2100b6799687f7b5f28ee9d82&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_017&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_49ceaf15d81094a0550fab7fdbf658a5897368ea823a969e2744dd825f6e7bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_018&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_685aea391daa2182e78b4a260cff0cda06a48d1701bdb8857001d2779bcd64c4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_019&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;direct_execution.sys.argv&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3aabd5921a1f574dba69160be63eb434bb3ccf93bf56414a439ed10f9853f51f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;module_evaluation.__name__&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_019 · value

Block: block_012; Operator: unknown.

IR inputs: 0: result_018, 1: 5

IR outputs: 0: result_020

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | Unlabeled data operation | placeholder | 0: D011; 1: D015 | — | 0: D009 |

Retained binding and explicit write changes: 

- `result: result_020`: Unbound → D009

<details><summary>Retained entry and exit evidence</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_8e844e5cb282c55c895e724b05e6451a5fced57a1593a04f23d6899b8c5a42cf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_016&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_92df6ad582519f16573ebfc5af0dc7c28be2c0e2100b6799687f7b5f28ee9d82&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_017&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_49ceaf15d81094a0550fab7fdbf658a5897368ea823a969e2744dd825f6e7bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_018&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_685aea391daa2182e78b4a260cff0cda06a48d1701bdb8857001d2779bcd64c4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_019&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;direct_execution.sys.argv&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3aabd5921a1f574dba69160be63eb434bb3ccf93bf56414a439ed10f9853f51f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;module_evaluation.__name__&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_8e844e5cb282c55c895e724b05e6451a5fced57a1593a04f23d6899b8c5a42cf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_016&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_92df6ad582519f16573ebfc5af0dc7c28be2c0e2100b6799687f7b5f28ee9d82&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_017&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_49ceaf15d81094a0550fab7fdbf658a5897368ea823a969e2744dd825f6e7bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_018&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_685aea391daa2182e78b4a260cff0cda06a48d1701bdb8857001d2779bcd64c4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_019&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_354c0f03477693bd70aa40ebe95e87f6ea4652e2acaabe77b088fa419d8cafb4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_020&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;direct_execution.sys.argv&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3aabd5921a1f574dba69160be63eb434bb3ccf93bf56414a439ed10f9853f51f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;module_evaluation.__name__&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 16,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 6
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 0,
                &quot;kind&quot;: &quot;input&quot;
              },
              {
                &quot;index&quot;: 1,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;kind&quot;: &quot;value&quot;,
            &quot;op&quot;: &quot;placeholder&quot;,
            &quot;output&quot;: &quot;function&quot;,
            &quot;reason&quot;: &quot;Define the callable with its imported requests binding and default count. The function-object constructor is outside the atomic vocabulary; its body does not execute here.&quot;
          }
        ],
        &quot;effect&quot;: null
      }
    ],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 16,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 6
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;function&quot;
        }
      }
    ],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 16,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 6
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;function&quot;
      }
    }
  ],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 16,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 6
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        },
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;kind&quot;: &quot;value&quot;,
      &quot;op&quot;: &quot;placeholder&quot;,
      &quot;output&quot;: &quot;function&quot;,
      &quot;reason&quot;: &quot;Define the callable with its imported requests binding and default count. The function-object constructor is outside the atomic vocabulary; its body does not execute here.&quot;
    }
  ]
}</pre>

</details>

## ir_020 · dispatch

Block: block_012; Operator: unknown.

IR inputs: []

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Retained binding and explicit write changes: 

- No retained binding change is shown; this does not imply absence of observation, sending or omitted historical bindings.

<details><summary>Retained entry and exit evidence</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_8e844e5cb282c55c895e724b05e6451a5fced57a1593a04f23d6899b8c5a42cf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_016&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_92df6ad582519f16573ebfc5af0dc7c28be2c0e2100b6799687f7b5f28ee9d82&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_017&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_49ceaf15d81094a0550fab7fdbf658a5897368ea823a969e2744dd825f6e7bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_018&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_685aea391daa2182e78b4a260cff0cda06a48d1701bdb8857001d2779bcd64c4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_019&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_354c0f03477693bd70aa40ebe95e87f6ea4652e2acaabe77b088fa419d8cafb4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_020&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;direct_execution.sys.argv&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3aabd5921a1f574dba69160be63eb434bb3ccf93bf56414a439ed10f9853f51f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;module_evaluation.__name__&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_8e844e5cb282c55c895e724b05e6451a5fced57a1593a04f23d6899b8c5a42cf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_016&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_92df6ad582519f16573ebfc5af0dc7c28be2c0e2100b6799687f7b5f28ee9d82&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_017&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_49ceaf15d81094a0550fab7fdbf658a5897368ea823a969e2744dd825f6e7bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_018&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_685aea391daa2182e78b4a260cff0cda06a48d1701bdb8857001d2779bcd64c4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_019&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_354c0f03477693bd70aa40ebe95e87f6ea4652e2acaabe77b088fa419d8cafb4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_020&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;direct_execution.sys.argv&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3aabd5921a1f574dba69160be63eb434bb3ccf93bf56414a439ed10f9853f51f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;module_evaluation.__name__&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_021 · receive

Block: block_013; Operator: unknown.

IR inputs: 0: module_evaluation.__name__

IR outputs: 0: result_021

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Retained binding and explicit write changes: 

- `result: result_021`: Unbound → D010

<details><summary>Retained entry and exit evidence</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_8e844e5cb282c55c895e724b05e6451a5fced57a1593a04f23d6899b8c5a42cf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_016&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_92df6ad582519f16573ebfc5af0dc7c28be2c0e2100b6799687f7b5f28ee9d82&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_017&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_49ceaf15d81094a0550fab7fdbf658a5897368ea823a969e2744dd825f6e7bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_018&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_685aea391daa2182e78b4a260cff0cda06a48d1701bdb8857001d2779bcd64c4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_019&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_354c0f03477693bd70aa40ebe95e87f6ea4652e2acaabe77b088fa419d8cafb4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_020&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;direct_execution.sys.argv&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3aabd5921a1f574dba69160be63eb434bb3ccf93bf56414a439ed10f9853f51f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;module_evaluation.__name__&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_8e844e5cb282c55c895e724b05e6451a5fced57a1593a04f23d6899b8c5a42cf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_016&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_92df6ad582519f16573ebfc5af0dc7c28be2c0e2100b6799687f7b5f28ee9d82&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_017&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_49ceaf15d81094a0550fab7fdbf658a5897368ea823a969e2744dd825f6e7bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_018&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_685aea391daa2182e78b4a260cff0cda06a48d1701bdb8857001d2779bcd64c4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_019&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_354c0f03477693bd70aa40ebe95e87f6ea4652e2acaabe77b088fa419d8cafb4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_020&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3aabd5921a1f574dba69160be63eb434bb3ccf93bf56414a439ed10f9853f51f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_021&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;direct_execution.sys.argv&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 18,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Acquire the module-evaluation name snapshot.&quot;,
            &quot;start_line&quot;: 18
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      }
    ],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 18,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Acquire the module-evaluation name snapshot.&quot;,
          &quot;start_line&quot;: 18
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      }
    }
  ],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_022 · dispatch

Block: block_013; Operator: unknown.

IR inputs: 0: result_021, 1: &quot;__main__&quot;

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    }
  ]
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | transform | compute | 0: D010; 1: D006 | — | 0: D031 |
| 2.1 | Unlabeled data operation | branch | 0: D031 | — | — |

Retained binding and explicit write changes: 

- No retained binding change is shown; this does not imply absence of observation, sending or omitted historical bindings.

<details><summary>Retained entry and exit evidence</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_8e844e5cb282c55c895e724b05e6451a5fced57a1593a04f23d6899b8c5a42cf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_016&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_92df6ad582519f16573ebfc5af0dc7c28be2c0e2100b6799687f7b5f28ee9d82&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_017&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_49ceaf15d81094a0550fab7fdbf658a5897368ea823a969e2744dd825f6e7bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_018&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_685aea391daa2182e78b4a260cff0cda06a48d1701bdb8857001d2779bcd64c4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_019&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_354c0f03477693bd70aa40ebe95e87f6ea4652e2acaabe77b088fa419d8cafb4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_020&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3aabd5921a1f574dba69160be63eb434bb3ccf93bf56414a439ed10f9853f51f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_021&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;direct_execution.sys.argv&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_8e844e5cb282c55c895e724b05e6451a5fced57a1593a04f23d6899b8c5a42cf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_016&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_92df6ad582519f16573ebfc5af0dc7c28be2c0e2100b6799687f7b5f28ee9d82&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_017&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_49ceaf15d81094a0550fab7fdbf658a5897368ea823a969e2744dd825f6e7bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_018&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_685aea391daa2182e78b4a260cff0cda06a48d1701bdb8857001d2779bcd64c4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_019&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_354c0f03477693bd70aa40ebe95e87f6ea4652e2acaabe77b088fa419d8cafb4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_020&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;direct_execution.sys.argv&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;dependencies&quot;: [
              &quot;possible&quot;,
              &quot;possible&quot;
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 18,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 18
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 0,
                &quot;kind&quot;: &quot;input&quot;
              },
              {
                &quot;index&quot;: 1,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;op&quot;: &quot;compute&quot;,
            &quot;output&quot;: &quot;is_main&quot;
          }
        ],
        &quot;effect&quot;: &quot;transform&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 18,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 18
          }
        ]
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 18,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 18
              }
            ],
            &quot;false_target&quot;: &quot;block_014&quot;,
            &quot;input&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;is_main&quot;
            },
            &quot;op&quot;: &quot;branch&quot;,
            &quot;predicate&quot;: &quot;truthy&quot;,
            &quot;true_target&quot;: &quot;block_015&quot;
          }
        ],
        &quot;effect&quot;: null
      }
    ],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 0
        }
      }
    ],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: [
    {
      &quot;dependencies&quot;: [
        &quot;possible&quot;,
        &quot;possible&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 18,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 18
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        },
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;is_main&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 18,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
          &quot;start_line&quot;: 18
        }
      ],
      &quot;false_target&quot;: &quot;block_014&quot;,
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;is_main&quot;
      },
      &quot;op&quot;: &quot;branch&quot;,
      &quot;predicate&quot;: &quot;truthy&quot;,
      &quot;true_target&quot;: &quot;block_015&quot;
    }
  ]
}</pre>

</details>

## ir_023 · return

Block: block_014; Operator: unknown.

IR inputs: 0: null

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Retained binding and explicit write changes: 

- No retained binding change is shown; this does not imply absence of observation, sending or omitted historical bindings.

<details><summary>Retained entry and exit evidence</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: []
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: []
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_024 · receive

Block: block_015; Operator: unknown.

IR inputs: 0: direct_execution.sys.argv

IR outputs: 0: result_022

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Retained binding and explicit write changes: 

- `result: result_022`: Unbound → D016

<details><summary>Retained entry and exit evidence</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_8e844e5cb282c55c895e724b05e6451a5fced57a1593a04f23d6899b8c5a42cf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_016&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_92df6ad582519f16573ebfc5af0dc7c28be2c0e2100b6799687f7b5f28ee9d82&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_017&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_49ceaf15d81094a0550fab7fdbf658a5897368ea823a969e2744dd825f6e7bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_018&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_685aea391daa2182e78b4a260cff0cda06a48d1701bdb8857001d2779bcd64c4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_019&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_354c0f03477693bd70aa40ebe95e87f6ea4652e2acaabe77b088fa419d8cafb4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_020&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;direct_execution.sys.argv&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_8e844e5cb282c55c895e724b05e6451a5fced57a1593a04f23d6899b8c5a42cf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_016&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_92df6ad582519f16573ebfc5af0dc7c28be2c0e2100b6799687f7b5f28ee9d82&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_017&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_49ceaf15d81094a0550fab7fdbf658a5897368ea823a969e2744dd825f6e7bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_018&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_685aea391daa2182e78b4a260cff0cda06a48d1701bdb8857001d2779bcd64c4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_019&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_354c0f03477693bd70aa40ebe95e87f6ea4652e2acaabe77b088fa419d8cafb4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_020&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_022&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 24,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Acquire this execution&#x27;s argv snapshot, retaining the whole object separately from subsequent cardinality and element selections.&quot;,
            &quot;start_line&quot;: 19
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      }
    ],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 24,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;Acquire this execution&#x27;s argv snapshot, retaining the whole object separately from subsequent cardinality and element selections.&quot;,
          &quot;start_line&quot;: 19
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      }
    }
  ],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_025 · dispatch

Block: block_015; Operator: unknown.

IR inputs: []

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Retained binding and explicit write changes: 

- No retained binding change is shown; this does not imply absence of observation, sending or omitted historical bindings.

<details><summary>Retained entry and exit evidence</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_8e844e5cb282c55c895e724b05e6451a5fced57a1593a04f23d6899b8c5a42cf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_016&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_92df6ad582519f16573ebfc5af0dc7c28be2c0e2100b6799687f7b5f28ee9d82&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_017&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_49ceaf15d81094a0550fab7fdbf658a5897368ea823a969e2744dd825f6e7bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_018&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_685aea391daa2182e78b4a260cff0cda06a48d1701bdb8857001d2779bcd64c4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_019&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_354c0f03477693bd70aa40ebe95e87f6ea4652e2acaabe77b088fa419d8cafb4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_020&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_022&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_8e844e5cb282c55c895e724b05e6451a5fced57a1593a04f23d6899b8c5a42cf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_016&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_92df6ad582519f16573ebfc5af0dc7c28be2c0e2100b6799687f7b5f28ee9d82&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_017&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_49ceaf15d81094a0550fab7fdbf658a5897368ea823a969e2744dd825f6e7bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_018&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_685aea391daa2182e78b4a260cff0cda06a48d1701bdb8857001d2779bcd64c4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_019&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_354c0f03477693bd70aa40ebe95e87f6ea4652e2acaabe77b088fa419d8cafb4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_020&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_022&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## Data index

| Short name | Complete ID | Content form |
|---|---|---|
| D001 | data_03788283a4a95be43be23e33579fedfad245022778073d07cfd54cadbd7b91d2 | opaque |
| D002 | data_118653532d696b9fa10931980ccc0f01faefcdc36d75d2934d500c1cc64c515c | loop_summary |
| D003 | data_137764b44213725de1784df71500123b046868f4761a48e30333bb3194c0e793 | opaque |
| D004 | data_1c0589d90480a256bda88a1a911db646a2eb65fdf672d470adedfd78785bb417 | loop_summary |
| D005 | data_220322fdf0ccf9c13756eceff32901373e751fcf1ee834315676c8dfca69304c | loop_summary |
| D006 | data_2e0489a7fb705e91bf28092a13ef8b6ee3f3e88b96001847a74950f877a2381f | literal |
| D007 | data_2f0ee426a970315ff5348642d81538c8ddc677f5045ea4d1840da5a9d73c6c77 | loop_summary |
| D008 | data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33 | opaque |
| D009 | data_354c0f03477693bd70aa40ebe95e87f6ea4652e2acaabe77b088fa419d8cafb4 | opaque |
| D010 | data_3aabd5921a1f574dba69160be63eb434bb3ccf93bf56414a439ed10f9853f51f | opaque |
| D011 | data_49ceaf15d81094a0550fab7fdbf658a5897368ea823a969e2744dd825f6e7bc3 | opaque |
| D012 | data_685aea391daa2182e78b4a260cff0cda06a48d1701bdb8857001d2779bcd64c4 | opaque |
| D013 | data_689fc477090c720437e9cab8439dda52e583e47500738ed1b7ce681bae70b8bf | loop_summary |
| D014 | data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1 | opaque |
| D015 | data_855d3559c34bac80abc0fe1e65c63e50e872274df655ce7190f3ca2544364268 | literal |
| D016 | data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a | opaque |
| D017 | data_8ad46ec08a65e1541e1723f48ae7fef23c54d06639f85acb507574ddf5405874 | loop_summary |
| D018 | data_8e6fad11c9faa98817e73a5a1a84ebf2e928314e1a52ca6cc7e6f8c5be2220ea | opaque |
| D019 | data_8e844e5cb282c55c895e724b05e6451a5fced57a1593a04f23d6899b8c5a42cf | opaque |
| D020 | data_92df6ad582519f16573ebfc5af0dc7c28be2c0e2100b6799687f7b5f28ee9d82 | opaque |
| D021 | data_9c233401d315759e046d494b00809f040bbcdac236e7cb45dea59a496056600f | loop_summary |
| D022 | data_a66a605573710f6a1c206756c81c9eab853d00915b3b4e117482ab9542e2c4bc | opaque |
| D023 | data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd | opaque |
| D024 | data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07 | opaque |
| D025 | data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74 | opaque |
| D026 | data_c54d71e7c232dcabd654cf4946eb941468b453170f70a1c2fc8df526c6303700 | loop_summary |
| D027 | data_cc5a1213aa56ef408a4aeecf69bc1f0f8904698f3d580b404c8423831523ad7c | literal |
| D028 | data_e196b331d4c8c645b18cee07b3350f19415e26bb29ab6673165814e91d61bba3 | opaque |
| D029 | data_f5a60accf4ec5fb97151b007d7347806a939744d7c207631620a8ebd1f97b926 | selection |
| D030 | data_fa1a82c2da5ba53f988d763ef9e72b191a3aaf8e615cdeeb24c0a9e60a8e0ce6 | literal |
| D031 | data_ffac727cb15fb8986e16eb1e9112604885fa7cfe403cfde181e9a6e9eae9c566 | opaque |

<details><summary>D001: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_03788283a4a95be43be23e33579fedfad245022778073d07cfd54cadbd7b91d2&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;runtime_context:google_search.invocation.bound.num_results&quot;,
    &quot;at&quot;: &quot;transfer:[\&quot;optional entry\&quot;,\&quot;runtime_context\&quot;,\&quot;google_search.invocation.bound.num_results\&quot;]&quot;,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D002: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;bindings&quot;: {
      &quot;argument-presence:3e4bfbe2b5313786baa1a30d858f7b40215d7f6809c5c7809a06d9c918c76b0f&quot;: &quot;0&quot;,
      &quot;selector:69e51028d0fab77b088e7669e6035a5e5c6e1655a2eab859e053e2906287226c:missing&quot;: &quot;1&quot;
    },
    &quot;form&quot;: &quot;loop_summary&quot;,
    &quot;producer&quot;: &quot;[\&quot;selector-route\&quot;,\&quot;data_f5a60accf4ec5fb97151b007d7347806a939744d7c207631620a8ebd1f97b926\&quot;]&quot;,
    &quot;scope&quot;: &quot;selector-route:data_f5a60accf4ec5fb97151b007d7347806a939744d7c207631620a8ebd1f97b926&quot;,
    &quot;variants&quot;: [
      {
        &quot;acquired_from&quot;: null,
        &quot;content&quot;: {
          &quot;base&quot;: &quot;data_f5a60accf4ec5fb97151b007d7347806a939744d7c207631620a8ebd1f97b926&quot;,
          &quot;form&quot;: &quot;selection&quot;,
          &quot;path&quot;: []
        },
        &quot;dependencies&quot;: [
          {
            &quot;data&quot;: &quot;data_f5a60accf4ec5fb97151b007d7347806a939744d7c207631620a8ebd1f97b926&quot;,
            &quot;relation&quot;: &quot;derived&quot;
          }
        ],
        &quot;inputs&quot;: [
          &quot;data_f5a60accf4ec5fb97151b007d7347806a939744d7c207631620a8ebd1f97b926&quot;
        ]
      }
    ]
  },
  &quot;id&quot;: &quot;data_118653532d696b9fa10931980ccc0f01faefcdc36d75d2934d500c1cc64c515c&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[\&quot;selector-route\&quot;,\&quot;data_f5a60accf4ec5fb97151b007d7347806a939744d7c207631620a8ebd1f97b926\&quot;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_f5a60accf4ec5fb97151b007d7347806a939744d7c207631620a8ebd1f97b926&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_f5a60accf4ec5fb97151b007d7347806a939744d7c207631620a8ebd1f97b926&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D003: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_137764b44213725de1784df71500123b046868f4761a48e30333bb3194c0e793&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 2, 0]&quot;,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D004: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;bindings&quot;: {
      &quot;argument-presence:3e4bfbe2b5313786baa1a30d858f7b40215d7f6809c5c7809a06d9c918c76b0f&quot;: &quot;1&quot;,
      &quot;selector:beafe61e33d890479bb611a34e4978f394509496692a9e23c836199284860f3f:missing&quot;: &quot;0&quot;
    },
    &quot;form&quot;: &quot;loop_summary&quot;,
    &quot;producer&quot;: &quot;[[\&quot;ir_003\&quot;,\&quot;input-use\&quot;,3],\&quot;stored-use\&quot;]&quot;,
    &quot;scope&quot;: &quot;selector-route:data_03788283a4a95be43be23e33579fedfad245022778073d07cfd54cadbd7b91d2&quot;,
    &quot;variants&quot;: [
      {
        &quot;acquired_from&quot;: null,
        &quot;content&quot;: {
          &quot;base&quot;: &quot;data_8ad46ec08a65e1541e1723f48ae7fef23c54d06639f85acb507574ddf5405874&quot;,
          &quot;form&quot;: &quot;selection&quot;,
          &quot;path&quot;: []
        },
        &quot;dependencies&quot;: [
          {
            &quot;data&quot;: &quot;data_8ad46ec08a65e1541e1723f48ae7fef23c54d06639f85acb507574ddf5405874&quot;,
            &quot;relation&quot;: &quot;derived&quot;
          }
        ],
        &quot;inputs&quot;: [
          &quot;data_8ad46ec08a65e1541e1723f48ae7fef23c54d06639f85acb507574ddf5405874&quot;
        ]
      }
    ]
  },
  &quot;id&quot;: &quot;data_1c0589d90480a256bda88a1a911db646a2eb65fdf672d470adedfd78785bb417&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[\&quot;ir_003\&quot;,\&quot;input-use\&quot;,3],\&quot;stored-use\&quot;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_8ad46ec08a65e1541e1723f48ae7fef23c54d06639f85acb507574ddf5405874&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_8ad46ec08a65e1541e1723f48ae7fef23c54d06639f85acb507574ddf5405874&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D005: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;bindings&quot;: {
      &quot;argument-presence:3e4bfbe2b5313786baa1a30d858f7b40215d7f6809c5c7809a06d9c918c76b0f&quot;: &quot;1&quot;,
      &quot;selector:beafe61e33d890479bb611a34e4978f394509496692a9e23c836199284860f3f:missing&quot;: &quot;0&quot;
    },
    &quot;form&quot;: &quot;loop_summary&quot;,
    &quot;producer&quot;: &quot;[\&quot;ir_007\&quot;,1,0]&quot;,
    &quot;scope&quot;: &quot;selector-route:data_03788283a4a95be43be23e33579fedfad245022778073d07cfd54cadbd7b91d2&quot;,
    &quot;variants&quot;: [
      {
        &quot;acquired_from&quot;: &quot;remote:https://www.googleapis.com/customsearch/v1&quot;,
        &quot;content&quot;: {
          &quot;form&quot;: &quot;opaque&quot;
        },
        &quot;dependencies&quot;: [
          {
            &quot;data&quot;: &quot;data_cc5a1213aa56ef408a4aeecf69bc1f0f8904698f3d580b404c8423831523ad7c&quot;,
            &quot;relation&quot;: &quot;possible&quot;
          },
          {
            &quot;data&quot;: &quot;data_c54d71e7c232dcabd654cf4946eb941468b453170f70a1c2fc8df526c6303700&quot;,
            &quot;relation&quot;: &quot;possible&quot;
          }
        ],
        &quot;inputs&quot;: [
          &quot;data_cc5a1213aa56ef408a4aeecf69bc1f0f8904698f3d580b404c8423831523ad7c&quot;,
          &quot;data_c54d71e7c232dcabd654cf4946eb941468b453170f70a1c2fc8df526c6303700&quot;
        ]
      }
    ]
  },
  &quot;id&quot;: &quot;data_220322fdf0ccf9c13756eceff32901373e751fcf1ee834315676c8dfca69304c&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;remote:https://www.googleapis.com/customsearch/v1&quot;,
    &quot;at&quot;: &quot;[\&quot;ir_007\&quot;,1,0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_c54d71e7c232dcabd654cf4946eb941468b453170f70a1c2fc8df526c6303700&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_cc5a1213aa56ef408a4aeecf69bc1f0f8904698f3d580b404c8423831523ad7c&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_c54d71e7c232dcabd654cf4946eb941468b453170f70a1c2fc8df526c6303700&quot;,
      &quot;data_cc5a1213aa56ef408a4aeecf69bc1f0f8904698f3d580b404c8423831523ad7c&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D006: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;literal&quot;,
    &quot;value&quot;: &quot;__main__&quot;
  },
  &quot;id&quot;: &quot;data_2e0489a7fb705e91bf28092a13ef8b6ee3f3e88b96001847a74950f877a2381f&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_022&#x27;, &#x27;input&#x27;, 1]&quot;,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D007: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;bindings&quot;: {
      &quot;argument-presence:3e4bfbe2b5313786baa1a30d858f7b40215d7f6809c5c7809a06d9c918c76b0f&quot;: &quot;0&quot;,
      &quot;selector:69e51028d0fab77b088e7669e6035a5e5c6e1655a2eab859e053e2906287226c:missing&quot;: &quot;1&quot;
    },
    &quot;form&quot;: &quot;loop_summary&quot;,
    &quot;producer&quot;: &quot;[[\&quot;ir_003\&quot;,\&quot;input-use\&quot;,3],\&quot;stored-use\&quot;]&quot;,
    &quot;scope&quot;: &quot;selector-route:data_f5a60accf4ec5fb97151b007d7347806a939744d7c207631620a8ebd1f97b926&quot;,
    &quot;variants&quot;: [
      {
        &quot;acquired_from&quot;: null,
        &quot;content&quot;: {
          &quot;base&quot;: &quot;data_118653532d696b9fa10931980ccc0f01faefcdc36d75d2934d500c1cc64c515c&quot;,
          &quot;form&quot;: &quot;selection&quot;,
          &quot;path&quot;: []
        },
        &quot;dependencies&quot;: [
          {
            &quot;data&quot;: &quot;data_118653532d696b9fa10931980ccc0f01faefcdc36d75d2934d500c1cc64c515c&quot;,
            &quot;relation&quot;: &quot;derived&quot;
          }
        ],
        &quot;inputs&quot;: [
          &quot;data_118653532d696b9fa10931980ccc0f01faefcdc36d75d2934d500c1cc64c515c&quot;
        ]
      }
    ]
  },
  &quot;id&quot;: &quot;data_2f0ee426a970315ff5348642d81538c8ddc677f5045ea4d1840da5a9d73c6c77&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[\&quot;ir_003\&quot;,\&quot;input-use\&quot;,3],\&quot;stored-use\&quot;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_118653532d696b9fa10931980ccc0f01faefcdc36d75d2934d500c1cc64c515c&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_118653532d696b9fa10931980ccc0f01faefcdc36d75d2934d500c1cc64c515c&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D008: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_2fa460ebf4b4375a758b6759d6392ebe044a28098945bede510f4f69a9d25b33&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;runtime_context:process environment: GOOGLE_API_KEY&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D009: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_354c0f03477693bd70aa40ebe95e87f6ea4652e2acaabe77b088fa419d8cafb4&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_019&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_49ceaf15d81094a0550fab7fdbf658a5897368ea823a969e2744dd825f6e7bc3&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_855d3559c34bac80abc0fe1e65c63e50e872274df655ce7190f3ca2544364268&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_49ceaf15d81094a0550fab7fdbf658a5897368ea823a969e2744dd825f6e7bc3&quot;,
      &quot;data_855d3559c34bac80abc0fe1e65c63e50e872274df655ce7190f3ca2544364268&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D010: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_3aabd5921a1f574dba69160be63eb434bb3ccf93bf56414a439ed10f9853f51f&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;runtime_context:module_evaluation.__name__&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D011: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_49ceaf15d81094a0550fab7fdbf658a5897368ea823a969e2744dd825f6e7bc3&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_017&#x27;, 2, 0]&quot;,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D012: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_685aea391daa2182e78b4a260cff0cda06a48d1701bdb8857001d2779bcd64c4&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_017&#x27;, 3, 0]&quot;,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D013: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;bindings&quot;: {
      &quot;argument-presence:3e4bfbe2b5313786baa1a30d858f7b40215d7f6809c5c7809a06d9c918c76b0f&quot;: &quot;0&quot;,
      &quot;selector:69e51028d0fab77b088e7669e6035a5e5c6e1655a2eab859e053e2906287226c:missing&quot;: &quot;1&quot;
    },
    &quot;form&quot;: &quot;loop_summary&quot;,
    &quot;producer&quot;: &quot;[[\&quot;ir_005\&quot;,0,0],\&quot;members\&quot;,[[\&quot;q\&quot;],[\&quot;key\&quot;],[\&quot;cx\&quot;],[\&quot;num\&quot;]]]&quot;,
    &quot;scope&quot;: &quot;selector-route:data_f5a60accf4ec5fb97151b007d7347806a939744d7c207631620a8ebd1f97b926&quot;,
    &quot;variants&quot;: [
      {
        &quot;acquired_from&quot;: null,
        &quot;content&quot;: {
          &quot;form&quot;: &quot;known_parts&quot;,
          &quot;parts&quot;: [
            {
              &quot;data&quot;: &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;,
              &quot;path&quot;: [
                &quot;q&quot;
              ]
            },
            {
              &quot;data&quot;: &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;,
              &quot;path&quot;: [
                &quot;key&quot;
              ]
            },
            {
              &quot;data&quot;: &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;,
              &quot;path&quot;: [
                &quot;cx&quot;
              ]
            },
            {
              &quot;data&quot;: &quot;data_2f0ee426a970315ff5348642d81538c8ddc677f5045ea4d1840da5a9d73c6c77&quot;,
              &quot;path&quot;: [
                &quot;num&quot;
              ]
            }
          ],
          &quot;parts_complete&quot;: true
        },
        &quot;dependencies&quot;: [
          {
            &quot;data&quot;: &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;,
            &quot;relation&quot;: &quot;derived&quot;
          },
          {
            &quot;data&quot;: &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;,
            &quot;relation&quot;: &quot;derived&quot;
          },
          {
            &quot;data&quot;: &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;,
            &quot;relation&quot;: &quot;derived&quot;
          },
          {
            &quot;data&quot;: &quot;data_2f0ee426a970315ff5348642d81538c8ddc677f5045ea4d1840da5a9d73c6c77&quot;,
            &quot;relation&quot;: &quot;derived&quot;
          }
        ],
        &quot;inputs&quot;: [
          &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;,
          &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;,
          &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;,
          &quot;data_2f0ee426a970315ff5348642d81538c8ddc677f5045ea4d1840da5a9d73c6c77&quot;
        ]
      }
    ]
  },
  &quot;id&quot;: &quot;data_689fc477090c720437e9cab8439dda52e583e47500738ed1b7ce681bae70b8bf&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[\&quot;ir_005\&quot;,0,0],\&quot;members\&quot;,[[\&quot;q\&quot;],[\&quot;key\&quot;],[\&quot;cx\&quot;],[\&quot;num\&quot;]]]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_2f0ee426a970315ff5348642d81538c8ddc677f5045ea4d1840da5a9d73c6c77&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_2f0ee426a970315ff5348642d81538c8ddc677f5045ea4d1840da5a9d73c6c77&quot;,
      &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;,
      &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;,
      &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D014: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_6af7aa11a0149a6a83316333995c306252b05ff4a9a31bd7b9f4222f8a537bb1&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;runtime_context:process environment: GOOGLE_CSE_ID&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D015: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;literal&quot;,
    &quot;value&quot;: 5
  },
  &quot;id&quot;: &quot;data_855d3559c34bac80abc0fe1e65c63e50e872274df655ce7190f3ca2544364268&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_019&#x27;, &#x27;input&#x27;, 1]&quot;,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D016: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_88df6da73e83b7768e9cd0aae15b437aecb81cbbb5da60e88887a5a75c3c425a&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;runtime_context:direct_execution.sys.argv&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D017: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;bindings&quot;: {
      &quot;argument-presence:3e4bfbe2b5313786baa1a30d858f7b40215d7f6809c5c7809a06d9c918c76b0f&quot;: &quot;1&quot;,
      &quot;selector:beafe61e33d890479bb611a34e4978f394509496692a9e23c836199284860f3f:missing&quot;: &quot;0&quot;
    },
    &quot;form&quot;: &quot;loop_summary&quot;,
    &quot;producer&quot;: &quot;[\&quot;selector-route\&quot;,\&quot;data_03788283a4a95be43be23e33579fedfad245022778073d07cfd54cadbd7b91d2\&quot;]&quot;,
    &quot;scope&quot;: &quot;selector-route:data_03788283a4a95be43be23e33579fedfad245022778073d07cfd54cadbd7b91d2&quot;,
    &quot;variants&quot;: [
      {
        &quot;acquired_from&quot;: null,
        &quot;content&quot;: {
          &quot;base&quot;: &quot;data_03788283a4a95be43be23e33579fedfad245022778073d07cfd54cadbd7b91d2&quot;,
          &quot;form&quot;: &quot;selection&quot;,
          &quot;path&quot;: []
        },
        &quot;dependencies&quot;: [
          {
            &quot;data&quot;: &quot;data_03788283a4a95be43be23e33579fedfad245022778073d07cfd54cadbd7b91d2&quot;,
            &quot;relation&quot;: &quot;derived&quot;
          }
        ],
        &quot;inputs&quot;: [
          &quot;data_03788283a4a95be43be23e33579fedfad245022778073d07cfd54cadbd7b91d2&quot;
        ]
      }
    ]
  },
  &quot;id&quot;: &quot;data_8ad46ec08a65e1541e1723f48ae7fef23c54d06639f85acb507574ddf5405874&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[\&quot;selector-route\&quot;,\&quot;data_03788283a4a95be43be23e33579fedfad245022778073d07cfd54cadbd7b91d2\&quot;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_03788283a4a95be43be23e33579fedfad245022778073d07cfd54cadbd7b91d2&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_03788283a4a95be43be23e33579fedfad245022778073d07cfd54cadbd7b91d2&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D018: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_8e6fad11c9faa98817e73a5a1a84ebf2e928314e1a52ca6cc7e6f8c5be2220ea&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 3, 0]&quot;,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D019: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_8e844e5cb282c55c895e724b05e6451a5fced57a1593a04f23d6899b8c5a42cf&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_017&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D020: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_92df6ad582519f16573ebfc5af0dc7c28be2c0e2100b6799687f7b5f28ee9d82&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_017&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D021: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;bindings&quot;: {
      &quot;argument-presence:3e4bfbe2b5313786baa1a30d858f7b40215d7f6809c5c7809a06d9c918c76b0f&quot;: &quot;0&quot;,
      &quot;selector:69e51028d0fab77b088e7669e6035a5e5c6e1655a2eab859e053e2906287226c:missing&quot;: &quot;1&quot;
    },
    &quot;form&quot;: &quot;loop_summary&quot;,
    &quot;producer&quot;: &quot;[\&quot;ir_007\&quot;,1,0]&quot;,
    &quot;scope&quot;: &quot;selector-route:data_f5a60accf4ec5fb97151b007d7347806a939744d7c207631620a8ebd1f97b926&quot;,
    &quot;variants&quot;: [
      {
        &quot;acquired_from&quot;: &quot;remote:https://www.googleapis.com/customsearch/v1&quot;,
        &quot;content&quot;: {
          &quot;form&quot;: &quot;opaque&quot;
        },
        &quot;dependencies&quot;: [
          {
            &quot;data&quot;: &quot;data_cc5a1213aa56ef408a4aeecf69bc1f0f8904698f3d580b404c8423831523ad7c&quot;,
            &quot;relation&quot;: &quot;possible&quot;
          },
          {
            &quot;data&quot;: &quot;data_689fc477090c720437e9cab8439dda52e583e47500738ed1b7ce681bae70b8bf&quot;,
            &quot;relation&quot;: &quot;possible&quot;
          }
        ],
        &quot;inputs&quot;: [
          &quot;data_cc5a1213aa56ef408a4aeecf69bc1f0f8904698f3d580b404c8423831523ad7c&quot;,
          &quot;data_689fc477090c720437e9cab8439dda52e583e47500738ed1b7ce681bae70b8bf&quot;
        ]
      }
    ]
  },
  &quot;id&quot;: &quot;data_9c233401d315759e046d494b00809f040bbcdac236e7cb45dea59a496056600f&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;remote:https://www.googleapis.com/customsearch/v1&quot;,
    &quot;at&quot;: &quot;[\&quot;ir_007\&quot;,1,0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_689fc477090c720437e9cab8439dda52e583e47500738ed1b7ce681bae70b8bf&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_cc5a1213aa56ef408a4aeecf69bc1f0f8904698f3d580b404c8423831523ad7c&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_689fc477090c720437e9cab8439dda52e583e47500738ed1b7ce681bae70b8bf&quot;,
      &quot;data_cc5a1213aa56ef408a4aeecf69bc1f0f8904698f3d580b404c8423831523ad7c&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D022: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_a66a605573710f6a1c206756c81c9eab853d00915b3b4e117482ab9542e2c4bc&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;runtime_context:analysis.activation_kind&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D023: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;runtime_context:google_search.invocation.bound.cse_id&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D024: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;runtime_context:google_search.invocation.bound.query&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D025: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;runtime_context:google_search.invocation.bound.api_key&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D026: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;bindings&quot;: {
      &quot;argument-presence:3e4bfbe2b5313786baa1a30d858f7b40215d7f6809c5c7809a06d9c918c76b0f&quot;: &quot;1&quot;,
      &quot;selector:beafe61e33d890479bb611a34e4978f394509496692a9e23c836199284860f3f:missing&quot;: &quot;0&quot;
    },
    &quot;form&quot;: &quot;loop_summary&quot;,
    &quot;producer&quot;: &quot;[[\&quot;ir_005\&quot;,0,0],\&quot;members\&quot;,[[\&quot;q\&quot;],[\&quot;key\&quot;],[\&quot;cx\&quot;],[\&quot;num\&quot;]]]&quot;,
    &quot;scope&quot;: &quot;selector-route:data_03788283a4a95be43be23e33579fedfad245022778073d07cfd54cadbd7b91d2&quot;,
    &quot;variants&quot;: [
      {
        &quot;acquired_from&quot;: null,
        &quot;content&quot;: {
          &quot;form&quot;: &quot;known_parts&quot;,
          &quot;parts&quot;: [
            {
              &quot;data&quot;: &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;,
              &quot;path&quot;: [
                &quot;q&quot;
              ]
            },
            {
              &quot;data&quot;: &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;,
              &quot;path&quot;: [
                &quot;key&quot;
              ]
            },
            {
              &quot;data&quot;: &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;,
              &quot;path&quot;: [
                &quot;cx&quot;
              ]
            },
            {
              &quot;data&quot;: &quot;data_1c0589d90480a256bda88a1a911db646a2eb65fdf672d470adedfd78785bb417&quot;,
              &quot;path&quot;: [
                &quot;num&quot;
              ]
            }
          ],
          &quot;parts_complete&quot;: true
        },
        &quot;dependencies&quot;: [
          {
            &quot;data&quot;: &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;,
            &quot;relation&quot;: &quot;derived&quot;
          },
          {
            &quot;data&quot;: &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;,
            &quot;relation&quot;: &quot;derived&quot;
          },
          {
            &quot;data&quot;: &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;,
            &quot;relation&quot;: &quot;derived&quot;
          },
          {
            &quot;data&quot;: &quot;data_1c0589d90480a256bda88a1a911db646a2eb65fdf672d470adedfd78785bb417&quot;,
            &quot;relation&quot;: &quot;derived&quot;
          }
        ],
        &quot;inputs&quot;: [
          &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;,
          &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;,
          &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;,
          &quot;data_1c0589d90480a256bda88a1a911db646a2eb65fdf672d470adedfd78785bb417&quot;
        ]
      }
    ]
  },
  &quot;id&quot;: &quot;data_c54d71e7c232dcabd654cf4946eb941468b453170f70a1c2fc8df526c6303700&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[\&quot;ir_005\&quot;,0,0],\&quot;members\&quot;,[[\&quot;q\&quot;],[\&quot;key\&quot;],[\&quot;cx\&quot;],[\&quot;num\&quot;]]]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_1c0589d90480a256bda88a1a911db646a2eb65fdf672d470adedfd78785bb417&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_1c0589d90480a256bda88a1a911db646a2eb65fdf672d470adedfd78785bb417&quot;,
      &quot;data_a758b1ed8eb44654d576a3ba88b25065234c4d9b026b377fdb3600b383dfa9dd&quot;,
      &quot;data_be3913aacdbb611be95938f6b9862a5a7b098adb7d0519cf7fa5e42aa505bf07&quot;,
      &quot;data_c12bd53aee99cd544bbe54ef9256f43558f15b4fc929bfd07c03bfb303a41a74&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D027: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;literal&quot;,
    &quot;value&quot;: &quot;https://www.googleapis.com/customsearch/v1&quot;
  },
  &quot;id&quot;: &quot;data_cc5a1213aa56ef408a4aeecf69bc1f0f8904698f3d580b404c8423831523ad7c&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_005&#x27;, &#x27;input&#x27;, 0]&quot;,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D028: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_e196b331d4c8c645b18cee07b3350f19415e26bb29ab6673165814e91d61bba3&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_002&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_a66a605573710f6a1c206756c81c9eab853d00915b3b4e117482ab9542e2c4bc&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_a66a605573710f6a1c206756c81c9eab853d00915b3b4e117482ab9542e2c4bc&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D029: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;base&quot;: &quot;data_fa1a82c2da5ba53f988d763ef9e72b191a3aaf8e615cdeeb24c0a9e60a8e0ce6&quot;,
    &quot;form&quot;: &quot;selection&quot;,
    &quot;path&quot;: [
      &quot;google_search.invocation.bound.num_results&quot;
    ]
  },
  &quot;id&quot;: &quot;data_f5a60accf4ec5fb97151b007d7347806a939744d7c207631620a8ebd1f97b926&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;omitted_argument&#x27;, &#x27;google_search.invocation.bound.num_results&#x27;]&quot;,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [
      &quot;data_fa1a82c2da5ba53f988d763ef9e72b191a3aaf8e615cdeeb24c0a9e60a8e0ce6&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D030: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;literal&quot;,
    &quot;value&quot;: {}
  },
  &quot;id&quot;: &quot;data_fa1a82c2da5ba53f988d763ef9e72b191a3aaf8e615cdeeb24c0a9e60a8e0ce6&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;omitted_argument&#x27;, &#x27;google_search.invocation.bound.num_results&#x27;]&quot;,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D031: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_ffac727cb15fb8986e16eb1e9112604885fa7cfe403cfde181e9a6e9eae9c566&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_022&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_3aabd5921a1f574dba69160be63eb434bb3ccf93bf56414a439ed10f9853f51f&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_2e0489a7fb705e91bf28092a13ef8b6ee3f3e88b96001847a74950f877a2381f&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_3aabd5921a1f574dba69160be63eb434bb3ccf93bf56414a439ed10f9853f51f&quot;,
      &quot;data_2e0489a7fb705e91bf28092a13ef8b6ee3f3e88b96001847a74950f877a2381f&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>


<details><summary>Separate audit materials: location evidence and solver statistics</summary>

<pre>{
  &quot;location_evidences&quot;: {
    &quot;api_key_environment&quot;: [
      {
        &quot;end_line&quot;: 27,
        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
        &quot;reason&quot;: &quot;The literal getenv key identifies this entry within process environment state.&quot;,
        &quot;start_line&quot;: 27
      },
      {
        &quot;reason&quot;: &quot;Runtime context defaults to task access and task retention.&quot;,
        &quot;rule_id&quot;: &quot;EM12&quot;
      }
    ],
    &quot;cse_id_environment&quot;: [
      {
        &quot;end_line&quot;: 28,
        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
        &quot;reason&quot;: &quot;The literal getenv key identifies this separate entry within process environment state.&quot;,
        &quot;start_line&quot;: 28
      },
      {
        &quot;reason&quot;: &quot;Runtime context defaults to task access and task retention.&quot;,
        &quot;rule_id&quot;: &quot;EM12&quot;
      }
    ],
    &quot;google_search_api&quot;: [
      {
        &quot;end_line&quot;: 14,
        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
        &quot;reason&quot;: &quot;The HTTPS URL and requests.get establish network transport to this endpoint.&quot;,
        &quot;start_line&quot;: 7
      },
      {
        &quot;reason&quot;: &quot;Remote access defaults to recipient scope; backend retention is not established.&quot;,
        &quot;rule_id&quot;: &quot;EM12&quot;
      }
    ],
    &quot;stdout&quot;: [
      {
        &quot;end_line&quot;: 38,
        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
        &quot;reason&quot;: &quot;print delivers the selected strings to process stdout. Its downstream consumer is unspecified.&quot;,
        &quot;start_line&quot;: 20
      },
      {
        &quot;reason&quot;: &quot;A process output stream does not establish network transport, human-facing output or model observation.&quot;,
        &quot;rule_id&quot;: &quot;EM06&quot;
      },
      {
        &quot;reason&quot;: &quot;Unspecified receiving deployment retains a recipient possibility; persistence is not established.&quot;,
        &quot;rule_id&quot;: &quot;EM12&quot;
      }
    ]
  },
  &quot;stats&quot;: {
    &quot;block_evaluation_counts&quot;: {
      &quot;block_001&quot;: 1,
      &quot;block_002&quot;: 1,
      &quot;block_003&quot;: 1,
      &quot;block_004&quot;: 1,
      &quot;block_005&quot;: 1,
      &quot;block_006&quot;: 1,
      &quot;block_011&quot;: 1,
      &quot;block_012&quot;: 1,
      &quot;block_013&quot;: 1,
      &quot;block_014&quot;: 1,
      &quot;block_015&quot;: 1,
      &quot;block_016&quot;: 1
    },
    &quot;block_evaluations&quot;: 12,
    &quot;block_relation_row_maxima&quot;: {
      &quot;block_001&quot;: 1,
      &quot;block_002&quot;: 1,
      &quot;block_003&quot;: 1,
      &quot;block_004&quot;: 1,
      &quot;block_005&quot;: 1,
      &quot;block_006&quot;: 1,
      &quot;block_011&quot;: 1,
      &quot;block_012&quot;: 1,
      &quot;block_013&quot;: 1,
      &quot;block_014&quot;: 1,
      &quot;block_015&quot;: 1,
      &quot;block_016&quot;: 1
    },
    &quot;compatible_candidates&quot;: 28,
    &quot;data_count&quot;: 31,
    &quot;dependency_wakeups&quot;: 0,
    &quot;description_revision&quot;: 8,
    &quot;edge_wakeups&quot;: 12,
    &quot;loop_families&quot;: 8,
    &quot;loop_relation_facts&quot;: 8,
    &quot;max_active_relation_rows&quot;: 12,
    &quot;max_block_relation_rows&quot;: 1,
    &quot;max_edge_relation_rows&quot;: 1,
    &quot;max_partition_rows&quot;: 1,
    &quot;partition_evaluations&quot;: 12,
    &quot;projected_locations_removed&quot;: 36,
    &quot;record_count&quot;: 18,
    &quot;registry_changed_keys&quot;: 22,
    &quot;removed_partitions&quot;: 0,
    &quot;scc_rebuilds&quot;: 0
  }
}</pre>

</details>

<details><summary>Compilation audit: original model processing segments and program-generated location mapping</summary>

<pre>{
  &quot;compilation_map&quot;: {
    &quot;compiled_sha256&quot;: &quot;753e9815bf80ed75e7f91ff0f0c8348fa04824b44ac1355631754f3c3c80a9df&quot;,
    &quot;compiler_version&quot;: &quot;skillflow-processing-compiler-v16&quot;,
    &quot;constraints&quot;: [
      {
        &quot;constraint_id&quot;: &quot;constraint_32737735255c5c82e64e&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/6/constraints/0&quot;,
        &quot;requirement_id&quot;: &quot;R7&quot;
      },
      {
        &quot;constraint_id&quot;: &quot;constraint_1397dcfff19ddc602aa3&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/7/constraints/0&quot;,
        &quot;requirement_id&quot;: &quot;R8&quot;
      },
      {
        &quot;constraint_id&quot;: &quot;constraint_87b8b3958b6d1cfa83f7&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/10/constraints/0&quot;,
        &quot;requirement_id&quot;: &quot;R11&quot;
      },
      {
        &quot;constraint_id&quot;: &quot;constraint_707a428c2c5cdcd00e6a&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/10/constraints/1&quot;,
        &quot;requirement_id&quot;: &quot;R11&quot;
      }
    ],
    &quot;events&quot;: [
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_002&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_002&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_002&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_002/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_002&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_002&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_002&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          1
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_002/segments/0/ops/1&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_005&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_005&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_005&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_005/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_007&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_007&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          1
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          2
        ],
        &quot;instruction_id&quot;: &quot;ir_007&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          2
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/1&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          3
        ],
        &quot;instruction_id&quot;: &quot;ir_007&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          3
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/2&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_008&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_008&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_008&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_008/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_011&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_011&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_011&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_011/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_014&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_014&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_014&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_014/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_017&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_017&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_017&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_017/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_017&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_017&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_017&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          1
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_017/segments/0/ops/1&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_017&quot;,
          &quot;events&quot;,
          2
        ],
        &quot;instruction_id&quot;: &quot;ir_017&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_017&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          2
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_017/segments/0/ops/2&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_017&quot;,
          &quot;events&quot;,
          3
        ],
        &quot;instruction_id&quot;: &quot;ir_017&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_017&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          3
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_017/segments/0/ops/3&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_019&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_019&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_019&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_019/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_022&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_022&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_022&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_022/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_022&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_022&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_022&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          1
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_022/segments/0/ops/1&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_027&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_027&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_027&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_027/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_027&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_027&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_027&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          1
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_027/segments/0/ops/1&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_030&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_030&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_030&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_030/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_031&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_031&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_031&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_031/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_031&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_031&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_031&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          1
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_031/segments/0/ops/1&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_033&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_033&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_033&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_033/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_037&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_037&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_037&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_037/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_039&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_039&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_039&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_039/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_041&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_041&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_041&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_041/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_042&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_042&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_042&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_042/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_042&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_042&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_042&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          1
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_042/segments/0/ops/1&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_047&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_047&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_047&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_047&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_047&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_047&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          1
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_047&quot;,
          &quot;events&quot;,
          2
        ],
        &quot;instruction_id&quot;: &quot;ir_047&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_047&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          2
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/1&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_047&quot;,
          &quot;events&quot;,
          3
        ],
        &quot;instruction_id&quot;: &quot;ir_047&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_047&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          3
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/2&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_048&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_048&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_048&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_048/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_050&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_050&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_050&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_050/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_052&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_052&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_052&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_052/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_054&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_054&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_054&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_054/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_055&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_055&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_055&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_055/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_055&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_055&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_055&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          1
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_055/segments/0/ops/1&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_055&quot;,
          &quot;events&quot;,
          2
        ],
        &quot;instruction_id&quot;: &quot;ir_055&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_055&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          2
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_055/segments/0/ops/2&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_056&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_056&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_056&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_056/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_058&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_058&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_058&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_058/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_059&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_059&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_059&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_059/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_059&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_059&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_059&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          1
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_059/segments/0/ops/1&quot;
      }
    ],
    &quot;fragment_origins&quot;: {
      &quot;/demands&quot;: &quot;task-correspondence&quot;,
      &quot;/expressions&quot;: &quot;processing&quot;,
      &quot;/ir_semantics&quot;: &quot;processing&quot;,
      &quot;/ir_semantics/ir_001/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_002/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_003/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_003/sensitivity/0&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_003/sensitivity/1&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_004/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_005/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_006/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_007/segments/0/ops/0/demands&quot;: &quot;task-correspondence&quot;,
      &quot;/ir_semantics/ir_007/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_008/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_009/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_011/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_012/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_014/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_015/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_016/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_017/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_018/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_019/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_020/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_021/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_022/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_023/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_024/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_025/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_027/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_029/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_030/segments/0/ops/0/demands&quot;: &quot;task-correspondence&quot;,
      &quot;/ir_semantics/ir_030/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_031/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_033/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_034/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_035/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_036/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_037/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_038/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_039/segments/0/ops/0/demands&quot;: &quot;task-correspondence&quot;,
      &quot;/ir_semantics/ir_039/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_039/sensitivity/0&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_040/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_041/segments/0/ops/0/demands&quot;: &quot;task-correspondence&quot;,
      &quot;/ir_semantics/ir_041/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_041/sensitivity/0&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_042/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_044/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_046/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_047/segments/0/ops/0/demands&quot;: &quot;task-correspondence&quot;,
      &quot;/ir_semantics/ir_047/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_048/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_050/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_052/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_054/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_055/segments/0/ops/0/demands&quot;: &quot;task-correspondence&quot;,
      &quot;/ir_semantics/ir_055/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_056/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_057/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_058/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_059/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_060/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_062/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/locations&quot;: &quot;processing&quot;,
      &quot;/processing_gaps&quot;: &quot;processing&quot;,
      &quot;/realizations&quot;: &quot;task-correspondence&quot;
    },
    &quot;fragment_paths&quot;: {
      &quot;/demands&quot;: {
        &quot;fragment&quot;: &quot;task-correspondence&quot;,
        &quot;path&quot;: &quot;/demands&quot;
      },
      &quot;/expressions&quot;: {
        &quot;fragment&quot;: &quot;processing&quot;,
        &quot;path&quot;: &quot;/expressions&quot;
      },
      &quot;/ir_semantics&quot;: {
        &quot;fragment&quot;: &quot;processing&quot;,
        &quot;path&quot;: &quot;/ir_semantics&quot;
      },
      &quot;/ir_semantics/ir_001/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_002/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_003/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_003/sensitivity/0&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations/0&quot;
      },
      &quot;/ir_semantics/ir_003/sensitivity/1&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations/1&quot;
      },
      &quot;/ir_semantics/ir_004/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_005/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_006/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_007/segments/0/ops/0/demands&quot;: {
        &quot;fragment&quot;: &quot;task-correspondence&quot;,
        &quot;path&quot;: &quot;/operation_demands/3/demands&quot;
      },
      &quot;/ir_semantics/ir_007/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_008/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_009/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_011/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_012/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_014/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_015/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_016/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_017/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_018/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_019/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_020/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_021/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_022/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_023/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_024/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_025/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_027/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_029/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_030/segments/0/ops/0/demands&quot;: {
        &quot;fragment&quot;: &quot;task-correspondence&quot;,
        &quot;path&quot;: &quot;/operation_demands/2/demands&quot;
      },
      &quot;/ir_semantics/ir_030/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_031/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_033/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_034/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_035/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_036/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_037/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_038/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_039/segments/0/ops/0/demands&quot;: {
        &quot;fragment&quot;: &quot;task-correspondence&quot;,
        &quot;path&quot;: &quot;/operation_demands/0/demands&quot;
      },
      &quot;/ir_semantics/ir_039/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_039/sensitivity/0&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations/2&quot;
      },
      &quot;/ir_semantics/ir_040/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_041/segments/0/ops/0/demands&quot;: {
        &quot;fragment&quot;: &quot;task-correspondence&quot;,
        &quot;path&quot;: &quot;/operation_demands/1/demands&quot;
      },
      &quot;/ir_semantics/ir_041/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_041/sensitivity/0&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations/3&quot;
      },
      &quot;/ir_semantics/ir_042/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_044/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_046/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_047/segments/0/ops/0/demands&quot;: {
        &quot;fragment&quot;: &quot;task-correspondence&quot;,
        &quot;path&quot;: &quot;/operation_demands/4/demands&quot;
      },
      &quot;/ir_semantics/ir_047/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_048/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_050/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_052/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_054/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_055/segments/0/ops/0/demands&quot;: {
        &quot;fragment&quot;: &quot;task-correspondence&quot;,
        &quot;path&quot;: &quot;/operation_demands/5/demands&quot;
      },
      &quot;/ir_semantics/ir_055/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_056/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_057/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_058/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_059/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_060/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_062/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/locations&quot;: {
        &quot;fragment&quot;: &quot;processing&quot;,
        &quot;path&quot;: &quot;/locations&quot;
      },
      &quot;/processing_gaps&quot;: {
        &quot;fragment&quot;: &quot;processing&quot;,
        &quot;path&quot;: &quot;/processing_gaps&quot;
      },
      &quot;/realizations&quot;: {
        &quot;fragment&quot;: &quot;task-correspondence&quot;,
        &quot;path&quot;: &quot;/realizations&quot;
      }
    },
    &quot;goals&quot;: [
      {
        &quot;goal_id&quot;: &quot;goal_30db5e138452cb9ef7d0&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R6&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_042&quot;,
          &quot;side&quot;: &quot;input&quot;
        },
        &quot;wire_pointer&quot;: &quot;/demands/0&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_6626a9b7006df51acfec&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/1&quot;,
        &quot;requirement_id&quot;: &quot;R6&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 1,
          &quot;instruction_id&quot;: &quot;ir_042&quot;,
          &quot;side&quot;: &quot;input&quot;
        },
        &quot;wire_pointer&quot;: &quot;/demands/1&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_5f7b0de1fbcd3cda3155&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/2&quot;,
        &quot;requirement_id&quot;: &quot;R6&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_043&quot;,
          &quot;path&quot;: []
        },
        &quot;wire_pointer&quot;: &quot;/demands/2&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_8dc2434700aa4f816628&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/3&quot;,
        &quot;requirement_id&quot;: &quot;R6&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_043&quot;,
          &quot;side&quot;: &quot;input&quot;
        },
        &quot;wire_pointer&quot;: &quot;/demands/3&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_f03501e2ae7bfe0fe880&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/4&quot;,
        &quot;requirement_id&quot;: &quot;R6&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 3,
          &quot;instruction_id&quot;: &quot;ir_043&quot;,
          &quot;side&quot;: &quot;input&quot;
        },
        &quot;wire_pointer&quot;: &quot;/demands/4&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_e27e65cb0973719f8d0c&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/5&quot;,
        &quot;requirement_id&quot;: &quot;R7&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 1,
          &quot;instruction_id&quot;: &quot;ir_026&quot;,
          &quot;side&quot;: &quot;input&quot;
        },
        &quot;wire_pointer&quot;: &quot;/demands/5&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_b1e5513bfa59bc391684&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/6&quot;,
        &quot;requirement_id&quot;: &quot;R7&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_028&quot;,
          &quot;path&quot;: []
        },
        &quot;wire_pointer&quot;: &quot;/demands/6&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_3031a78c1ef4112f5143&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/7&quot;,
        &quot;requirement_id&quot;: &quot;R7&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_028&quot;,
          &quot;side&quot;: &quot;input&quot;
        },
        &quot;wire_pointer&quot;: &quot;/demands/7&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_03c014430f620dc30bc1&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/8&quot;,
        &quot;requirement_id&quot;: &quot;R7&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 3,
          &quot;instruction_id&quot;: &quot;ir_028&quot;,
          &quot;side&quot;: &quot;input&quot;
        },
        &quot;wire_pointer&quot;: &quot;/demands/8&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_c7f4a0f978b9d168d100&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/9&quot;,
        &quot;requirement_id&quot;: &quot;R8&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_032&quot;,
          &quot;path&quot;: []
        },
        &quot;wire_pointer&quot;: &quot;/demands/9&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_3b72a96af1875583c39c&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/10&quot;,
        &quot;requirement_id&quot;: &quot;R8&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_032&quot;,
          &quot;side&quot;: &quot;input&quot;
        },
        &quot;wire_pointer&quot;: &quot;/demands/10&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_b0b5137951839411af3a&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/11&quot;,
        &quot;requirement_id&quot;: &quot;R8&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_035&quot;,
          &quot;side&quot;: &quot;output&quot;
        },
        &quot;wire_pointer&quot;: &quot;/demands/11&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_40f5d1bed30228dfd6e4&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/12&quot;,
        &quot;requirement_id&quot;: &quot;R8&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_037&quot;,
          &quot;side&quot;: &quot;output&quot;
        },
        &quot;wire_pointer&quot;: &quot;/demands/12&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_0be000d4810f8f3c0222&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/13&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 1,
          &quot;instruction_id&quot;: &quot;ir_045&quot;,
          &quot;side&quot;: &quot;input&quot;
        },
        &quot;wire_pointer&quot;: &quot;/demands/13&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_0421fb460b2c4d01ffce&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/14&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 2,
          &quot;instruction_id&quot;: &quot;ir_045&quot;,
          &quot;side&quot;: &quot;input&quot;
        },
        &quot;wire_pointer&quot;: &quot;/demands/14&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_7dd3044d52d25e64260f&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/15&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 3,
          &quot;instruction_id&quot;: &quot;ir_045&quot;,
          &quot;side&quot;: &quot;input&quot;
        },
        &quot;wire_pointer&quot;: &quot;/demands/15&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_55ae4281dcbda7d84fe4&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/16&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 4,
          &quot;instruction_id&quot;: &quot;ir_045&quot;,
          &quot;side&quot;: &quot;input&quot;
        },
        &quot;wire_pointer&quot;: &quot;/demands/16&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_dad55038fb65295e2c7e&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/17&quot;,
        &quot;requirement_id&quot;: &quot;R10&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_053&quot;,
          &quot;path&quot;: []
        },
        &quot;wire_pointer&quot;: &quot;/demands/17&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_7f6e057c984a9470337b&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/18&quot;,
        &quot;requirement_id&quot;: &quot;R10&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_053&quot;,
          &quot;side&quot;: &quot;input&quot;
        },
        &quot;wire_pointer&quot;: &quot;/demands/18&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_c12cafebb167f326ee0a&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/19&quot;,
        &quot;requirement_id&quot;: &quot;R10&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_053&quot;,
          &quot;side&quot;: &quot;output&quot;
        },
        &quot;wire_pointer&quot;: &quot;/demands/19&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_4b0e48909b41d5504eef&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/20&quot;,
        &quot;requirement_id&quot;: &quot;R11&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_010&quot;,
          &quot;path&quot;: []
        },
        &quot;wire_pointer&quot;: &quot;/demands/20&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_85f2aca5480afeb418ae&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/21&quot;,
        &quot;requirement_id&quot;: &quot;R11&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_049&quot;,
          &quot;path&quot;: []
        },
        &quot;wire_pointer&quot;: &quot;/demands/21&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_531dfe512418609f85fd&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/22&quot;,
        &quot;requirement_id&quot;: &quot;R11&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_061&quot;,
          &quot;path&quot;: []
        },
        &quot;wire_pointer&quot;: &quot;/demands/22&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_092103370d62b9cf7908&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/23&quot;,
        &quot;requirement_id&quot;: &quot;R11&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 1,
          &quot;instruction_id&quot;: &quot;ir_061&quot;,
          &quot;side&quot;: &quot;output&quot;
        },
        &quot;wire_pointer&quot;: &quot;/demands/23&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_78a7ed31ff14c44a06ce&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/24&quot;,
        &quot;requirement_id&quot;: &quot;R11&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 6,
          &quot;instruction_id&quot;: &quot;ir_061&quot;,
          &quot;side&quot;: &quot;input&quot;
        },
        &quot;wire_pointer&quot;: &quot;/demands/24&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_7499ca086a1ca251ccd2&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_007&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;kind&quot;: &quot;self&quot;
          }
        },
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0/demands/0&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_f203aaf75e859fe8eea7&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/1&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_007&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 0,
            &quot;kind&quot;: &quot;input&quot;
          }
        },
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0/demands/1&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_a53a79ed4bc4bfaf680c&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/2&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_007&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 1,
            &quot;kind&quot;: &quot;input&quot;
          }
        },
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0/demands/2&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_193cd7bd9fb036404428&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/3&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_007&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 1,
            &quot;kind&quot;: &quot;input&quot;
          }
        },
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0/demands/3&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_3430728c31d0e042e784&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/4&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_007&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 1,
            &quot;kind&quot;: &quot;input&quot;
          }
        },
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0/demands/4&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_cdb0a25d8a9150034d0f&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/5&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_007&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 1,
            &quot;kind&quot;: &quot;input&quot;
          }
        },
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0/demands/5&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_4ad0eab07154c1aaa2b9&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_030/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R7&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_030&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;kind&quot;: &quot;output&quot;
          }
        },
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_030/segments/0/ops/0/demands/0&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_70acc2008a32f28053da&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_039/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R6&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_039&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;kind&quot;: &quot;self&quot;
          }
        },
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_039/segments/0/ops/0/demands/0&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_f70fc4b44c037f830a98&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_041/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R6&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_041&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;kind&quot;: &quot;self&quot;
          }
        },
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_041/segments/0/ops/0/demands/0&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_42ed4aa2cdb2100ed88c&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_047/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_047&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;kind&quot;: &quot;self&quot;
          }
        },
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0/demands/0&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_70798a4339ad5b9bf591&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_047/events/0/events/0/atomic_ops/0/demands/1&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_047&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 0,
            &quot;kind&quot;: &quot;input&quot;
          }
        },
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0/demands/1&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_a17798157b31d33c3ccf&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_047/events/0/events/0/atomic_ops/0/demands/2&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_047&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 1,
            &quot;kind&quot;: &quot;input&quot;
          }
        },
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0/demands/2&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_0ff2d8705fe31571833e&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_047/events/0/events/0/atomic_ops/0/demands/3&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_047&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 1,
            &quot;kind&quot;: &quot;input&quot;
          }
        },
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0/demands/3&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_103aaf31c24991fc045d&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_047/events/0/events/0/atomic_ops/0/demands/4&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_047&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 1,
            &quot;kind&quot;: &quot;input&quot;
          }
        },
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0/demands/4&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_afa101e151fe0e62e625&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_047/events/0/events/0/atomic_ops/0/demands/5&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_047&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 1,
            &quot;kind&quot;: &quot;input&quot;
          }
        },
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0/demands/5&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_be84fe1ab10539c2456b&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_055/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R10&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_055&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;kind&quot;: &quot;self&quot;
          }
        },
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_055/segments/0/ops/0/demands/0&quot;
      },
      {
        &quot;goal_id&quot;: &quot;goal_448b50a2c066ce83b49d&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_055/events/0/events/0/atomic_ops/0/demands/1&quot;,
        &quot;requirement_id&quot;: &quot;R10&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_055&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 0,
            &quot;kind&quot;: &quot;input&quot;
          }
        },
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_055/segments/0/ops/0/demands/1&quot;
      }
    ],
    &quot;input_contracts&quot;: [
      {
        &quot;contract_id&quot;: &quot;input_contract_1905eb77e70f72300523&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_055/events/0/events/0/atomic_ops/0/input_contract&quot;,
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_055/segments/0/ops/0/input_contract&quot;
      },
      {
        &quot;contract_id&quot;: &quot;input_contract_3e2e2ce7a0aa38492cdf&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_047/events/0/events/1/atomic_ops/0/input_contract&quot;,
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0/input_contract&quot;
      },
      {
        &quot;contract_id&quot;: &quot;input_contract_4b0fba93e9d0621251ef&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_042/events/0/events/0/atomic_ops/0/demand_transfer&quot;,
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_042/segments/0/ops/0/demand_transfer&quot;
      },
      {
        &quot;contract_id&quot;: &quot;input_contract_5377ea9647295532d401&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/input_contract&quot;,
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0/input_contract&quot;
      },
      {
        &quot;contract_id&quot;: &quot;input_contract_575643478bb33c25da5d&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_047/events/0/events/0/atomic_ops/0/input_contract&quot;,
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0/input_contract&quot;
      },
      {
        &quot;contract_id&quot;: &quot;input_contract_60103276e1fc611e1490&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_059/events/0/events/0/atomic_ops/0/demand_transfer&quot;,
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_059/segments/0/ops/0/demand_transfer&quot;
      },
      {
        &quot;contract_id&quot;: &quot;input_contract_7c872f5a134199a1f6a6&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/input_contract&quot;,
        &quot;wire_pointer&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0/input_contract&quot;
      }
    ],
    &quot;processing_gaps&quot;: [
      {
        &quot;control&quot;: true,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 18,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 6
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_002&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The abstract activation selector has no supplied concrete encoding. Its Boolean placeholder preserves the CFG&#x27;s two supported activation choices without inventing a source-level test.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 16,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 14
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_007&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          1,
          2
        ],
        &quot;reason&quot;: &quot;The atomic call form exposes one normal response, not separately correlated exception and completion outputs. Source-backed placeholders retain this call&#x27;s exceptional value and Boolean control. Their availability remains restricted by the original CFG&#x27;s normal and exceptional continuations.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: true,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 16,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 15
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_010&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          0,
          1
        ],
        &quot;reason&quot;: &quot;Requests&#x27; internal status predicate and exception construction are absent. The local invocation effect and its outcome placeholders retain the status-check boundary; no response.json call occurs on the exceptional continuation.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 16,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 16
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_013&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          1,
          2
        ],
        &quot;reason&quot;: &quot;The normal decoded version and exceptional outcome belong to this same response.json invocation. The primitive vocabulary does not jointly bind those conditional outputs, so exception and completion placeholders retain their source occurrence and CFG-restricted availability.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 24,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 24
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_032&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          2,
          3
        ],
        &quot;reason&quot;: &quot;The conversion&#x27;s actual exception and normal-completion control require conditional outcome slots beyond the scalar compute result. Placeholders preserve those slots; neither successful integers nor request results supply the exception.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 19,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 15
          },
          {
            &quot;end_line&quot;: 28,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 27
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_039&quot;,
        &quot;locations&quot;: [
          &quot;api_key_environment&quot;
        ],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The Skill requires credential storage in a workspace .env file, but the implementation supplies no file loader or other file-to-process-environment handoff. This read therefore has process-environment provenance only; no file read, file ownership or storage execution is inferred.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 19,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 15
          },
          {
            &quot;end_line&quot;: 28,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 28
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_041&quot;,
        &quot;locations&quot;: [
          &quot;cse_id_environment&quot;
        ],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The documented .env entry and this environment lookup are not connected by an evidenced loader. The environment value remains distinct from any hypothetical stored-file version.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 28,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 26
          },
          {
            &quot;end_line&quot;: 35,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 23
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_045&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The example invokes skills/google-search/scripts/search.py, whereas the supplied implementation is skill/scripts/search.py. Their relationship is unestablished. If the command reaches this CLI, its query and credentials bind to the corresponding slots and its omitted count selects 5; execution of that handoff is not asserted.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 14,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 14
          },
          {
            &quot;end_line&quot;: 37,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 34
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_047&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          1,
          2
        ],
        &quot;reason&quot;: &quot;The normal HTTP response and actual raised exception are alternative outcomes of this CLI helper request. Outcome placeholders preserve this occurrence and the CFG-restricted availability, rather than treating an exception as successful API content.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: true,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 15,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 15
          },
          {
            &quot;end_line&quot;: 37,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 35
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_049&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          0,
          1
        ],
        &quot;reason&quot;: &quot;The supplied source does not expose Requests&#x27; internal status predicate or exception construction. The local effect and outcome placeholders preserve this helper invocation&#x27;s status check and its alternative continuation.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 16,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 16
          },
          {
            &quot;end_line&quot;: 37,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 35
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_051&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          1,
          2
        ],
        &quot;reason&quot;: &quot;Conditional exception and completion slots are retained with local placeholders for this decoding occurrence. They do not replace, alias or originate from its successful decoded content.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 37,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 35
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_053&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          2,
          3
        ],
        &quot;reason&quot;: &quot;Serialization&#x27;s conditional exception and completion slots are represented by source-backed placeholders. A serialization failure preserves the already received decoded results binding and supplies no successful formatted string.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 38,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 36
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_055&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          0,
          1
        ],
        &quot;reason&quot;: &quot;Print may raise after partial delivery. Outcome placeholders retain the actual print exception and normal-completion control; the supplied source establishes neither an exact delivered prefix nor rollback.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 28,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 21
          },
          {
            &quot;end_line&quot;: 39,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 6
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_057&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The Workflow is a placeholder. No per-element traversal, yield collection, save, later file read, retry, summarization or application-level shared-state update is supplied. No saved-result provenance or downstream model routing can be attached to this completion.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: true,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 39,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 37
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_061&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;Error conversion and printing may themselves fail outside the protected try body. Their concrete exceptional payloads are not CFG outputs here; sys.exit(1) is reached only after those handler actions complete normally.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_061&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;str_e&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_061/action_bindings&quot;
          },
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;error_sys_exit&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_061/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_053&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;json_dumps&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_053/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_051&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;cli.response_json&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_051/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_049&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;cli.raise_for_status&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_049/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_045&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;google_search_call&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_045/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_043&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;credential_sys_exit&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_043/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_032&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;int_count&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_032/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_028&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;usage_sys_exit&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_028/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_026&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;cli.argv_length&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_026/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_013&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;public.response_json&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_013/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_010&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;public.raise_for_status&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_010/action_bindings&quot;
          }
        ]
      }
    ],
    &quot;raw_sha256&quot;: &quot;a28a1b85da5942fd9281f3a815ad4424ea04396bdf3686117516026ba98edc22&quot;,
    &quot;runtime_contract&quot;: {
      &quot;sha256&quot;: &quot;3c5e26ebc288fbba41176d1a9e3b7eef1132f5aacc23fe69a3535665f5b711f9&quot;,
      &quot;version&quot;: &quot;skillflow-abstract-runtime-v14&quot;
    },
    &quot;schema_version&quot;: &quot;skillflow-processing-compilation-v16&quot;,
    &quot;source_action_bindings&quot;: {
      &quot;ir_001&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;receive&quot;,
            &quot;ref&quot;: &quot;activation.acquire&quot;,
            &quot;role&quot;: &quot;receive&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 18,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 6
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;activation.acquire&quot;: [
            [
              &quot;output_bindings&quot;,
              0
            ]
          ]
        }
      },
      &quot;ir_002&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;branch&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 18,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 6
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              1
            ],
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_003&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;receive&quot;,
            &quot;ref&quot;: &quot;public.acquire_parameters&quot;,
            &quot;role&quot;: &quot;receive&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 6,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 6
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;public.acquire_parameters&quot;: [
            [
              &quot;output_bindings&quot;,
              0
            ],
            [
              &quot;output_bindings&quot;,
              1
            ],
            [
              &quot;output_bindings&quot;,
              2
            ],
            [
              &quot;output_bindings&quot;,
              3
            ]
          ]
        }
      },
      &quot;ir_004&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 7,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 6
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_005&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;value&quot;,
            &quot;ref&quot;: &quot;public.prepare_request&quot;,
            &quot;role&quot;: &quot;value&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 13,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 7
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;public.prepare_request&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;output_bindings&quot;,
              0
            ],
            [
              &quot;output_bindings&quot;,
              1
            ]
          ]
        }
      },
      &quot;ir_006&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 14,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 13
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_007&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;call&quot;,
            &quot;ref&quot;: &quot;public.requests_get&quot;,
            &quot;role&quot;: &quot;call&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 14,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 14
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;public.requests_get&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              1
            ],
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              2
            ],
            [
              &quot;output_bindings&quot;,
              0
            ],
            [
              &quot;output_bindings&quot;,
              1
            ],
            [
              &quot;output_bindings&quot;,
              2
            ]
          ]
        }
      },
      &quot;ir_008&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;branch&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 14,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 14
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_009&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;return&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 14,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 14
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_011&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;branch&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 15,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 15
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_012&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;return&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 15,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 15
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_014&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;branch&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 16,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 16
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_015&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;return&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 16,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 16
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_016&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;return&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 16,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 16
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_017&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;import&quot;,
            &quot;ref&quot;: &quot;import_sys&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 1,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 1
            }
          },
          {
            &quot;kind&quot;: &quot;import&quot;,
            &quot;ref&quot;: &quot;import_json&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 2,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 2
            }
          },
          {
            &quot;kind&quot;: &quot;import&quot;,
            &quot;ref&quot;: &quot;import_requests&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 3,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 3
            }
          },
          {
            &quot;kind&quot;: &quot;import&quot;,
            &quot;ref&quot;: &quot;import_os&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 4,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 4
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;import_json&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              1
            ],
            [
              &quot;output_bindings&quot;,
              1
            ]
          ],
          &quot;import_os&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              3
            ],
            [
              &quot;output_bindings&quot;,
              3
            ]
          ],
          &quot;import_requests&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              2
            ],
            [
              &quot;output_bindings&quot;,
              2
            ]
          ],
          &quot;import_sys&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;output_bindings&quot;,
              0
            ]
          ]
        }
      },
      &quot;ir_018&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 6,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 4
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_019&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;value&quot;,
            &quot;ref&quot;: &quot;module.bind_google_search&quot;,
            &quot;role&quot;: &quot;value&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 16,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 6
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;module.bind_google_search&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;output_bindings&quot;,
              0
            ]
          ]
        }
      },
      &quot;ir_020&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 18,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 16
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_021&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;receive&quot;,
            &quot;ref&quot;: &quot;module.acquire_name&quot;,
            &quot;role&quot;: &quot;receive&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 18,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 18
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;module.acquire_name&quot;: [
            [
              &quot;output_bindings&quot;,
              0
            ]
          ]
        }
      },
      &quot;ir_022&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;branch&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 18,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 18
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              1
            ],
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_023&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;return&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 39,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 18
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_024&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;receive&quot;,
            &quot;ref&quot;: &quot;cli.acquire_argv&quot;,
            &quot;role&quot;: &quot;receive&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 24,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 19
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;cli.acquire_argv&quot;: [
            [
              &quot;output_bindings&quot;,
              0
            ]
          ]
        }
      },
      &quot;ir_025&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 19,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 19
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_027&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;branch&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 19,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 19
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              1
            ],
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_029&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;return&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 21,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 21
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_030&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;value&quot;,
            &quot;ref&quot;: &quot;cli.query_projection&quot;,
            &quot;role&quot;: &quot;value&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 23,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 23
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;cli.query_projection&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;output_bindings&quot;,
              0
            ]
          ]
        }
      },
      &quot;ir_031&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;branch&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 24,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 24
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              1
            ],
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_033&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;branch&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 24,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 24
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_034&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;return&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 24,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 24
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_035&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;value&quot;,
            &quot;ref&quot;: &quot;cli.default_count&quot;,
            &quot;role&quot;: &quot;value&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 24,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 24
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;cli.default_count&quot;: [
            [
              &quot;output_bindings&quot;,
              0
            ]
          ]
        }
      },
      &quot;ir_036&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 24,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 24
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_037&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;value&quot;,
            &quot;ref&quot;: &quot;cli.bind_num_results&quot;,
            &quot;role&quot;: &quot;value&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 24,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 24
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;cli.bind_num_results&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;output_bindings&quot;,
              0
            ]
          ]
        }
      },
      &quot;ir_038&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 27,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 24
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_039&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;read&quot;,
            &quot;ref&quot;: &quot;cli.getenv_api_key&quot;,
            &quot;role&quot;: &quot;read&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 27,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 27
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;cli.getenv_api_key&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;output_bindings&quot;,
              0
            ]
          ]
        }
      },
      &quot;ir_040&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 28,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 27
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_041&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;read&quot;,
            &quot;ref&quot;: &quot;cli.getenv_cse_id&quot;,
            &quot;role&quot;: &quot;read&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 28,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 28
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;cli.getenv_cse_id&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;output_bindings&quot;,
              0
            ]
          ]
        }
      },
      &quot;ir_042&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;branch&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 30,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 30
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              1
            ],
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_044&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;return&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 32,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 32
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_046&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 14,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 13
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_047&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;call&quot;,
            &quot;ref&quot;: &quot;cli.requests_get&quot;,
            &quot;role&quot;: &quot;call&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 14,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 14
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;cli.requests_get&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              1
            ],
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              2
            ],
            [
              &quot;output_bindings&quot;,
              0
            ],
            [
              &quot;output_bindings&quot;,
              1
            ],
            [
              &quot;output_bindings&quot;,
              2
            ]
          ]
        }
      },
      &quot;ir_048&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;branch&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 14,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 14
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_050&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;branch&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 15,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 15
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_052&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;branch&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 16,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 16
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_054&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;branch&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 36,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 36
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_055&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;deliver&quot;,
            &quot;ref&quot;: &quot;cli.print_formatted_json&quot;,
            &quot;role&quot;: &quot;deliver&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 36,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 36
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;cli.print_formatted_json&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              1
            ],
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              2
            ],
            [
              &quot;output_bindings&quot;,
              0
            ],
            [
              &quot;output_bindings&quot;,
              1
            ]
          ]
        }
      },
      &quot;ir_056&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;branch&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 36,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 36
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_057&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;return&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 39,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 34
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_058&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;value&quot;,
            &quot;ref&quot;: &quot;cli.select_raised_exception&quot;,
            &quot;role&quot;: &quot;value&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 37,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 37
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;cli.select_raised_exception&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;output_bindings&quot;,
              0
            ]
          ]
        }
      },
      &quot;ir_059&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;dispatch&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;branch&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 37,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 37
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              0
            ],
            [
              &quot;segments&quot;,
              0,
              &quot;ops&quot;,
              1
            ],
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_060&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;return&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 37,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 37
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      },
      &quot;ir_062&quot;: {
        &quot;actions&quot;: [
          {
            &quot;kind&quot;: &quot;return&quot;,
            &quot;ref&quot;: &quot;exit&quot;,
            &quot;role&quot;: &quot;other&quot;,
            &quot;source&quot;: {
              &quot;end_line&quot;: 39,
              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
              &quot;start_line&quot;: 39
            }
          }
        ],
        &quot;bindings&quot;: {
          &quot;exit&quot;: [
            [
              &quot;terminator&quot;
            ]
          ]
        }
      }
    },
    &quot;wire_paths&quot;: {
      &quot;/ir_semantics/ir_001&quot;: &quot;/ir_semantics/ir_001&quot;,
      &quot;/ir_semantics/ir_001/output_bindings/0&quot;: &quot;/ir_semantics/ir_001/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_001/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_001/evidences&quot;,
      &quot;/ir_semantics/ir_002&quot;: &quot;/ir_semantics/ir_002&quot;,
      &quot;/ir_semantics/ir_002/events/0&quot;: &quot;/ir_semantics/ir_002/segments/0&quot;,
      &quot;/ir_semantics/ir_002/events/0/events/0&quot;: &quot;/ir_semantics/ir_002/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_002/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_002/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_002/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_002/segments/0/ops/0/evidences&quot;,
      &quot;/ir_semantics/ir_002/events/0/events/1&quot;: &quot;/ir_semantics/ir_002/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_002/events/0/events/1/atomic_ops/0&quot;: &quot;/ir_semantics/ir_002/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_002/events/0/events/1/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_002/evidences&quot;,
      &quot;/ir_semantics/ir_002/events/0/evidences&quot;: &quot;/ir_semantics/ir_002/evidences&quot;,
      &quot;/ir_semantics/ir_003&quot;: &quot;/ir_semantics/ir_003&quot;,
      &quot;/ir_semantics/ir_003/output_bindings/0&quot;: &quot;/ir_semantics/ir_003/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_003/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_003/evidences&quot;,
      &quot;/ir_semantics/ir_003/output_bindings/1&quot;: &quot;/ir_semantics/ir_003/output_bindings/1&quot;,
      &quot;/ir_semantics/ir_003/output_bindings/1/evidences&quot;: &quot;/ir_semantics/ir_003/evidences&quot;,
      &quot;/ir_semantics/ir_003/output_bindings/2&quot;: &quot;/ir_semantics/ir_003/output_bindings/2&quot;,
      &quot;/ir_semantics/ir_003/output_bindings/2/evidences&quot;: &quot;/ir_semantics/ir_003/evidences&quot;,
      &quot;/ir_semantics/ir_003/output_bindings/3&quot;: &quot;/ir_semantics/ir_003/output_bindings/3&quot;,
      &quot;/ir_semantics/ir_003/output_bindings/3/evidences&quot;: &quot;/ir_semantics/ir_003/evidences&quot;,
      &quot;/ir_semantics/ir_004&quot;: &quot;/ir_semantics/ir_004&quot;,
      &quot;/ir_semantics/ir_005&quot;: &quot;/ir_semantics/ir_005&quot;,
      &quot;/ir_semantics/ir_005/events/0&quot;: &quot;/ir_semantics/ir_005/segments/0&quot;,
      &quot;/ir_semantics/ir_005/events/0/events/0&quot;: &quot;/ir_semantics/ir_005/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_005/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_005/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_005/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_005/evidences&quot;,
      &quot;/ir_semantics/ir_005/events/0/evidences&quot;: &quot;/ir_semantics/ir_005/evidences&quot;,
      &quot;/ir_semantics/ir_005/output_bindings/0&quot;: &quot;/ir_semantics/ir_005/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_005/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_005/evidences&quot;,
      &quot;/ir_semantics/ir_005/output_bindings/1&quot;: &quot;/ir_semantics/ir_005/output_bindings/1&quot;,
      &quot;/ir_semantics/ir_005/output_bindings/1/evidences&quot;: &quot;/ir_semantics/ir_005/evidences&quot;,
      &quot;/ir_semantics/ir_006&quot;: &quot;/ir_semantics/ir_006&quot;,
      &quot;/ir_semantics/ir_007&quot;: &quot;/ir_semantics/ir_007&quot;,
      &quot;/ir_semantics/ir_007/events/0&quot;: &quot;/ir_semantics/ir_007/segments/0&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/0&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/0&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0/demands/0&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/1&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0/demands/1&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/2&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0/demands/2&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/3&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0/demands/3&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/4&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0/demands/4&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/5&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0/demands/5&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_007/evidences&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/1&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/1/atomic_ops/0&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_007/evidences&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/2&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/2/atomic_ops/0&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/2/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/1/evidences&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/3&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/2&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/3/atomic_ops/0&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/2&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/3/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/2/evidences&quot;,
      &quot;/ir_semantics/ir_007/events/0/evidences&quot;: &quot;/ir_semantics/ir_007/evidences&quot;,
      &quot;/ir_semantics/ir_007/output_bindings/0&quot;: &quot;/ir_semantics/ir_007/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_007/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_007/evidences&quot;,
      &quot;/ir_semantics/ir_007/output_bindings/1&quot;: &quot;/ir_semantics/ir_007/output_bindings/1&quot;,
      &quot;/ir_semantics/ir_007/output_bindings/1/evidences&quot;: &quot;/ir_semantics/ir_007/evidences&quot;,
      &quot;/ir_semantics/ir_007/output_bindings/2&quot;: &quot;/ir_semantics/ir_007/output_bindings/2&quot;,
      &quot;/ir_semantics/ir_007/output_bindings/2/evidences&quot;: &quot;/ir_semantics/ir_007/evidences&quot;,
      &quot;/ir_semantics/ir_008&quot;: &quot;/ir_semantics/ir_008&quot;,
      &quot;/ir_semantics/ir_008/events/0&quot;: &quot;/ir_semantics/ir_008/segments/0&quot;,
      &quot;/ir_semantics/ir_008/events/0/events/0&quot;: &quot;/ir_semantics/ir_008/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_008/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_008/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_008/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_008/evidences&quot;,
      &quot;/ir_semantics/ir_008/events/0/evidences&quot;: &quot;/ir_semantics/ir_008/evidences&quot;,
      &quot;/ir_semantics/ir_009&quot;: &quot;/ir_semantics/ir_009&quot;,
      &quot;/ir_semantics/ir_011&quot;: &quot;/ir_semantics/ir_011&quot;,
      &quot;/ir_semantics/ir_011/events/0&quot;: &quot;/ir_semantics/ir_011/segments/0&quot;,
      &quot;/ir_semantics/ir_011/events/0/events/0&quot;: &quot;/ir_semantics/ir_011/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_011/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_011/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_011/evidences&quot;,
      &quot;/ir_semantics/ir_011/events/0/evidences&quot;: &quot;/ir_semantics/ir_011/evidences&quot;,
      &quot;/ir_semantics/ir_012&quot;: &quot;/ir_semantics/ir_012&quot;,
      &quot;/ir_semantics/ir_014&quot;: &quot;/ir_semantics/ir_014&quot;,
      &quot;/ir_semantics/ir_014/events/0&quot;: &quot;/ir_semantics/ir_014/segments/0&quot;,
      &quot;/ir_semantics/ir_014/events/0/events/0&quot;: &quot;/ir_semantics/ir_014/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_014/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_014/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_014/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_014/evidences&quot;,
      &quot;/ir_semantics/ir_014/events/0/evidences&quot;: &quot;/ir_semantics/ir_014/evidences&quot;,
      &quot;/ir_semantics/ir_015&quot;: &quot;/ir_semantics/ir_015&quot;,
      &quot;/ir_semantics/ir_016&quot;: &quot;/ir_semantics/ir_016&quot;,
      &quot;/ir_semantics/ir_017&quot;: &quot;/ir_semantics/ir_017&quot;,
      &quot;/ir_semantics/ir_017/events/0&quot;: &quot;/ir_semantics/ir_017/segments/0&quot;,
      &quot;/ir_semantics/ir_017/events/0/events/0&quot;: &quot;/ir_semantics/ir_017/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_017/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_017/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_017/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_017/segments/0/ops/0/evidences&quot;,
      &quot;/ir_semantics/ir_017/events/0/events/1&quot;: &quot;/ir_semantics/ir_017/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_017/events/0/events/1/atomic_ops/0&quot;: &quot;/ir_semantics/ir_017/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_017/events/0/events/1/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_017/segments/0/ops/1/evidences&quot;,
      &quot;/ir_semantics/ir_017/events/0/events/2&quot;: &quot;/ir_semantics/ir_017/segments/0/ops/2&quot;,
      &quot;/ir_semantics/ir_017/events/0/events/2/atomic_ops/0&quot;: &quot;/ir_semantics/ir_017/segments/0/ops/2&quot;,
      &quot;/ir_semantics/ir_017/events/0/events/2/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_017/segments/0/ops/2/evidences&quot;,
      &quot;/ir_semantics/ir_017/events/0/events/3&quot;: &quot;/ir_semantics/ir_017/segments/0/ops/3&quot;,
      &quot;/ir_semantics/ir_017/events/0/events/3/atomic_ops/0&quot;: &quot;/ir_semantics/ir_017/segments/0/ops/3&quot;,
      &quot;/ir_semantics/ir_017/events/0/events/3/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_017/segments/0/ops/3/evidences&quot;,
      &quot;/ir_semantics/ir_017/events/0/evidences&quot;: &quot;/ir_semantics/ir_017/evidences&quot;,
      &quot;/ir_semantics/ir_017/output_bindings/0&quot;: &quot;/ir_semantics/ir_017/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_017/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_017/evidences&quot;,
      &quot;/ir_semantics/ir_017/output_bindings/1&quot;: &quot;/ir_semantics/ir_017/output_bindings/1&quot;,
      &quot;/ir_semantics/ir_017/output_bindings/1/evidences&quot;: &quot;/ir_semantics/ir_017/evidences&quot;,
      &quot;/ir_semantics/ir_017/output_bindings/2&quot;: &quot;/ir_semantics/ir_017/output_bindings/2&quot;,
      &quot;/ir_semantics/ir_017/output_bindings/2/evidences&quot;: &quot;/ir_semantics/ir_017/evidences&quot;,
      &quot;/ir_semantics/ir_017/output_bindings/3&quot;: &quot;/ir_semantics/ir_017/output_bindings/3&quot;,
      &quot;/ir_semantics/ir_017/output_bindings/3/evidences&quot;: &quot;/ir_semantics/ir_017/evidences&quot;,
      &quot;/ir_semantics/ir_018&quot;: &quot;/ir_semantics/ir_018&quot;,
      &quot;/ir_semantics/ir_019&quot;: &quot;/ir_semantics/ir_019&quot;,
      &quot;/ir_semantics/ir_019/events/0&quot;: &quot;/ir_semantics/ir_019/segments/0&quot;,
      &quot;/ir_semantics/ir_019/events/0/events/0&quot;: &quot;/ir_semantics/ir_019/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_019/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_019/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_019/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_019/segments/0/ops/0/evidences&quot;,
      &quot;/ir_semantics/ir_019/events/0/evidences&quot;: &quot;/ir_semantics/ir_019/evidences&quot;,
      &quot;/ir_semantics/ir_019/output_bindings/0&quot;: &quot;/ir_semantics/ir_019/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_019/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_019/evidences&quot;,
      &quot;/ir_semantics/ir_020&quot;: &quot;/ir_semantics/ir_020&quot;,
      &quot;/ir_semantics/ir_021&quot;: &quot;/ir_semantics/ir_021&quot;,
      &quot;/ir_semantics/ir_021/output_bindings/0&quot;: &quot;/ir_semantics/ir_021/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_021/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_021/evidences&quot;,
      &quot;/ir_semantics/ir_022&quot;: &quot;/ir_semantics/ir_022&quot;,
      &quot;/ir_semantics/ir_022/events/0&quot;: &quot;/ir_semantics/ir_022/segments/0&quot;,
      &quot;/ir_semantics/ir_022/events/0/events/0&quot;: &quot;/ir_semantics/ir_022/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_022/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_022/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_022/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_022/evidences&quot;,
      &quot;/ir_semantics/ir_022/events/0/events/1&quot;: &quot;/ir_semantics/ir_022/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_022/events/0/events/1/atomic_ops/0&quot;: &quot;/ir_semantics/ir_022/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_022/events/0/events/1/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_022/evidences&quot;,
      &quot;/ir_semantics/ir_022/events/0/evidences&quot;: &quot;/ir_semantics/ir_022/evidences&quot;,
      &quot;/ir_semantics/ir_023&quot;: &quot;/ir_semantics/ir_023&quot;,
      &quot;/ir_semantics/ir_024&quot;: &quot;/ir_semantics/ir_024&quot;,
      &quot;/ir_semantics/ir_024/output_bindings/0&quot;: &quot;/ir_semantics/ir_024/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_024/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_024/evidences&quot;,
      &quot;/ir_semantics/ir_025&quot;: &quot;/ir_semantics/ir_025&quot;,
      &quot;/ir_semantics/ir_027&quot;: &quot;/ir_semantics/ir_027&quot;,
      &quot;/ir_semantics/ir_027/events/0&quot;: &quot;/ir_semantics/ir_027/segments/0&quot;,
      &quot;/ir_semantics/ir_027/events/0/events/0&quot;: &quot;/ir_semantics/ir_027/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_027/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_027/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_027/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_027/evidences&quot;,
      &quot;/ir_semantics/ir_027/events/0/events/1&quot;: &quot;/ir_semantics/ir_027/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_027/events/0/events/1/atomic_ops/0&quot;: &quot;/ir_semantics/ir_027/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_027/events/0/events/1/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_027/evidences&quot;,
      &quot;/ir_semantics/ir_027/events/0/evidences&quot;: &quot;/ir_semantics/ir_027/evidences&quot;,
      &quot;/ir_semantics/ir_029&quot;: &quot;/ir_semantics/ir_029&quot;,
      &quot;/ir_semantics/ir_030&quot;: &quot;/ir_semantics/ir_030&quot;,
      &quot;/ir_semantics/ir_030/events/0&quot;: &quot;/ir_semantics/ir_030/segments/0&quot;,
      &quot;/ir_semantics/ir_030/events/0/events/0&quot;: &quot;/ir_semantics/ir_030/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_030/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_030/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_030/events/0/events/0/atomic_ops/0/demands/0&quot;: &quot;/ir_semantics/ir_030/segments/0/ops/0/demands/0&quot;,
      &quot;/ir_semantics/ir_030/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_030/evidences&quot;,
      &quot;/ir_semantics/ir_030/events/0/evidences&quot;: &quot;/ir_semantics/ir_030/evidences&quot;,
      &quot;/ir_semantics/ir_030/output_bindings/0&quot;: &quot;/ir_semantics/ir_030/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_030/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_030/evidences&quot;,
      &quot;/ir_semantics/ir_031&quot;: &quot;/ir_semantics/ir_031&quot;,
      &quot;/ir_semantics/ir_031/events/0&quot;: &quot;/ir_semantics/ir_031/segments/0&quot;,
      &quot;/ir_semantics/ir_031/events/0/events/0&quot;: &quot;/ir_semantics/ir_031/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_031/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_031/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_031/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_031/evidences&quot;,
      &quot;/ir_semantics/ir_031/events/0/events/1&quot;: &quot;/ir_semantics/ir_031/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_031/events/0/events/1/atomic_ops/0&quot;: &quot;/ir_semantics/ir_031/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_031/events/0/events/1/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_031/evidences&quot;,
      &quot;/ir_semantics/ir_031/events/0/evidences&quot;: &quot;/ir_semantics/ir_031/evidences&quot;,
      &quot;/ir_semantics/ir_033&quot;: &quot;/ir_semantics/ir_033&quot;,
      &quot;/ir_semantics/ir_033/events/0&quot;: &quot;/ir_semantics/ir_033/segments/0&quot;,
      &quot;/ir_semantics/ir_033/events/0/events/0&quot;: &quot;/ir_semantics/ir_033/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_033/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_033/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_033/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_033/evidences&quot;,
      &quot;/ir_semantics/ir_033/events/0/evidences&quot;: &quot;/ir_semantics/ir_033/evidences&quot;,
      &quot;/ir_semantics/ir_034&quot;: &quot;/ir_semantics/ir_034&quot;,
      &quot;/ir_semantics/ir_035&quot;: &quot;/ir_semantics/ir_035&quot;,
      &quot;/ir_semantics/ir_035/output_bindings/0&quot;: &quot;/ir_semantics/ir_035/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_035/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_035/evidences&quot;,
      &quot;/ir_semantics/ir_036&quot;: &quot;/ir_semantics/ir_036&quot;,
      &quot;/ir_semantics/ir_037&quot;: &quot;/ir_semantics/ir_037&quot;,
      &quot;/ir_semantics/ir_037/events/0&quot;: &quot;/ir_semantics/ir_037/segments/0&quot;,
      &quot;/ir_semantics/ir_037/events/0/events/0&quot;: &quot;/ir_semantics/ir_037/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_037/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_037/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_037/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_037/evidences&quot;,
      &quot;/ir_semantics/ir_037/events/0/evidences&quot;: &quot;/ir_semantics/ir_037/evidences&quot;,
      &quot;/ir_semantics/ir_037/output_bindings/0&quot;: &quot;/ir_semantics/ir_037/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_037/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_037/evidences&quot;,
      &quot;/ir_semantics/ir_038&quot;: &quot;/ir_semantics/ir_038&quot;,
      &quot;/ir_semantics/ir_039&quot;: &quot;/ir_semantics/ir_039&quot;,
      &quot;/ir_semantics/ir_039/events/0&quot;: &quot;/ir_semantics/ir_039/segments/0&quot;,
      &quot;/ir_semantics/ir_039/events/0/events/0&quot;: &quot;/ir_semantics/ir_039/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_039/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_039/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_039/events/0/events/0/atomic_ops/0/demands/0&quot;: &quot;/ir_semantics/ir_039/segments/0/ops/0/demands/0&quot;,
      &quot;/ir_semantics/ir_039/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_039/evidences&quot;,
      &quot;/ir_semantics/ir_039/events/0/evidences&quot;: &quot;/ir_semantics/ir_039/evidences&quot;,
      &quot;/ir_semantics/ir_039/output_bindings/0&quot;: &quot;/ir_semantics/ir_039/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_039/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_039/evidences&quot;,
      &quot;/ir_semantics/ir_040&quot;: &quot;/ir_semantics/ir_040&quot;,
      &quot;/ir_semantics/ir_041&quot;: &quot;/ir_semantics/ir_041&quot;,
      &quot;/ir_semantics/ir_041/events/0&quot;: &quot;/ir_semantics/ir_041/segments/0&quot;,
      &quot;/ir_semantics/ir_041/events/0/events/0&quot;: &quot;/ir_semantics/ir_041/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_041/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_041/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_041/events/0/events/0/atomic_ops/0/demands/0&quot;: &quot;/ir_semantics/ir_041/segments/0/ops/0/demands/0&quot;,
      &quot;/ir_semantics/ir_041/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_041/evidences&quot;,
      &quot;/ir_semantics/ir_041/events/0/evidences&quot;: &quot;/ir_semantics/ir_041/evidences&quot;,
      &quot;/ir_semantics/ir_041/output_bindings/0&quot;: &quot;/ir_semantics/ir_041/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_041/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_041/evidences&quot;,
      &quot;/ir_semantics/ir_042&quot;: &quot;/ir_semantics/ir_042&quot;,
      &quot;/ir_semantics/ir_042/events/0&quot;: &quot;/ir_semantics/ir_042/segments/0&quot;,
      &quot;/ir_semantics/ir_042/events/0/events/0&quot;: &quot;/ir_semantics/ir_042/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_042/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_042/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_042/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_042/evidences&quot;,
      &quot;/ir_semantics/ir_042/events/0/events/1&quot;: &quot;/ir_semantics/ir_042/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_042/events/0/events/1/atomic_ops/0&quot;: &quot;/ir_semantics/ir_042/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_042/events/0/events/1/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_042/evidences&quot;,
      &quot;/ir_semantics/ir_042/events/0/evidences&quot;: &quot;/ir_semantics/ir_042/evidences&quot;,
      &quot;/ir_semantics/ir_044&quot;: &quot;/ir_semantics/ir_044&quot;,
      &quot;/ir_semantics/ir_046&quot;: &quot;/ir_semantics/ir_046&quot;,
      &quot;/ir_semantics/ir_047&quot;: &quot;/ir_semantics/ir_047&quot;,
      &quot;/ir_semantics/ir_047/events/0&quot;: &quot;/ir_semantics/ir_047/segments/0&quot;,
      &quot;/ir_semantics/ir_047/events/0/events/0&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_047/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_047/events/0/events/0/atomic_ops/0/demands/0&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0/demands/0&quot;,
      &quot;/ir_semantics/ir_047/events/0/events/0/atomic_ops/0/demands/1&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0/demands/1&quot;,
      &quot;/ir_semantics/ir_047/events/0/events/0/atomic_ops/0/demands/2&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0/demands/2&quot;,
      &quot;/ir_semantics/ir_047/events/0/events/0/atomic_ops/0/demands/3&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0/demands/3&quot;,
      &quot;/ir_semantics/ir_047/events/0/events/0/atomic_ops/0/demands/4&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0/demands/4&quot;,
      &quot;/ir_semantics/ir_047/events/0/events/0/atomic_ops/0/demands/5&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0/demands/5&quot;,
      &quot;/ir_semantics/ir_047/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_047/evidences&quot;,
      &quot;/ir_semantics/ir_047/events/0/events/1&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_047/events/0/events/1/atomic_ops/0&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_047/events/0/events/1/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_047/evidences&quot;,
      &quot;/ir_semantics/ir_047/events/0/events/2&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_047/events/0/events/2/atomic_ops/0&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_047/events/0/events/2/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/1/evidences&quot;,
      &quot;/ir_semantics/ir_047/events/0/events/3&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/2&quot;,
      &quot;/ir_semantics/ir_047/events/0/events/3/atomic_ops/0&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/2&quot;,
      &quot;/ir_semantics/ir_047/events/0/events/3/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_047/segments/0/ops/2/evidences&quot;,
      &quot;/ir_semantics/ir_047/events/0/evidences&quot;: &quot;/ir_semantics/ir_047/evidences&quot;,
      &quot;/ir_semantics/ir_047/output_bindings/0&quot;: &quot;/ir_semantics/ir_047/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_047/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_047/evidences&quot;,
      &quot;/ir_semantics/ir_047/output_bindings/1&quot;: &quot;/ir_semantics/ir_047/output_bindings/1&quot;,
      &quot;/ir_semantics/ir_047/output_bindings/1/evidences&quot;: &quot;/ir_semantics/ir_047/evidences&quot;,
      &quot;/ir_semantics/ir_047/output_bindings/2&quot;: &quot;/ir_semantics/ir_047/output_bindings/2&quot;,
      &quot;/ir_semantics/ir_047/output_bindings/2/evidences&quot;: &quot;/ir_semantics/ir_047/evidences&quot;,
      &quot;/ir_semantics/ir_048&quot;: &quot;/ir_semantics/ir_048&quot;,
      &quot;/ir_semantics/ir_048/events/0&quot;: &quot;/ir_semantics/ir_048/segments/0&quot;,
      &quot;/ir_semantics/ir_048/events/0/events/0&quot;: &quot;/ir_semantics/ir_048/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_048/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_048/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_048/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_048/evidences&quot;,
      &quot;/ir_semantics/ir_048/events/0/evidences&quot;: &quot;/ir_semantics/ir_048/evidences&quot;,
      &quot;/ir_semantics/ir_050&quot;: &quot;/ir_semantics/ir_050&quot;,
      &quot;/ir_semantics/ir_050/events/0&quot;: &quot;/ir_semantics/ir_050/segments/0&quot;,
      &quot;/ir_semantics/ir_050/events/0/events/0&quot;: &quot;/ir_semantics/ir_050/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_050/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_050/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_050/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_050/evidences&quot;,
      &quot;/ir_semantics/ir_050/events/0/evidences&quot;: &quot;/ir_semantics/ir_050/evidences&quot;,
      &quot;/ir_semantics/ir_052&quot;: &quot;/ir_semantics/ir_052&quot;,
      &quot;/ir_semantics/ir_052/events/0&quot;: &quot;/ir_semantics/ir_052/segments/0&quot;,
      &quot;/ir_semantics/ir_052/events/0/events/0&quot;: &quot;/ir_semantics/ir_052/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_052/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_052/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_052/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_052/evidences&quot;,
      &quot;/ir_semantics/ir_052/events/0/evidences&quot;: &quot;/ir_semantics/ir_052/evidences&quot;,
      &quot;/ir_semantics/ir_054&quot;: &quot;/ir_semantics/ir_054&quot;,
      &quot;/ir_semantics/ir_054/events/0&quot;: &quot;/ir_semantics/ir_054/segments/0&quot;,
      &quot;/ir_semantics/ir_054/events/0/events/0&quot;: &quot;/ir_semantics/ir_054/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_054/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_054/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_054/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_054/evidences&quot;,
      &quot;/ir_semantics/ir_054/events/0/evidences&quot;: &quot;/ir_semantics/ir_054/evidences&quot;,
      &quot;/ir_semantics/ir_055&quot;: &quot;/ir_semantics/ir_055&quot;,
      &quot;/ir_semantics/ir_055/events/0&quot;: &quot;/ir_semantics/ir_055/segments/0&quot;,
      &quot;/ir_semantics/ir_055/events/0/events/0&quot;: &quot;/ir_semantics/ir_055/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_055/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_055/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_055/events/0/events/0/atomic_ops/0/demands/0&quot;: &quot;/ir_semantics/ir_055/segments/0/ops/0/demands/0&quot;,
      &quot;/ir_semantics/ir_055/events/0/events/0/atomic_ops/0/demands/1&quot;: &quot;/ir_semantics/ir_055/segments/0/ops/0/demands/1&quot;,
      &quot;/ir_semantics/ir_055/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_055/evidences&quot;,
      &quot;/ir_semantics/ir_055/events/0/events/1&quot;: &quot;/ir_semantics/ir_055/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_055/events/0/events/1/atomic_ops/0&quot;: &quot;/ir_semantics/ir_055/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_055/events/0/events/1/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_055/segments/0/ops/1/evidences&quot;,
      &quot;/ir_semantics/ir_055/events/0/events/2&quot;: &quot;/ir_semantics/ir_055/segments/0/ops/2&quot;,
      &quot;/ir_semantics/ir_055/events/0/events/2/atomic_ops/0&quot;: &quot;/ir_semantics/ir_055/segments/0/ops/2&quot;,
      &quot;/ir_semantics/ir_055/events/0/events/2/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_055/segments/0/ops/2/evidences&quot;,
      &quot;/ir_semantics/ir_055/events/0/evidences&quot;: &quot;/ir_semantics/ir_055/evidences&quot;,
      &quot;/ir_semantics/ir_055/output_bindings/0&quot;: &quot;/ir_semantics/ir_055/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_055/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_055/evidences&quot;,
      &quot;/ir_semantics/ir_055/output_bindings/1&quot;: &quot;/ir_semantics/ir_055/output_bindings/1&quot;,
      &quot;/ir_semantics/ir_055/output_bindings/1/evidences&quot;: &quot;/ir_semantics/ir_055/evidences&quot;,
      &quot;/ir_semantics/ir_056&quot;: &quot;/ir_semantics/ir_056&quot;,
      &quot;/ir_semantics/ir_056/events/0&quot;: &quot;/ir_semantics/ir_056/segments/0&quot;,
      &quot;/ir_semantics/ir_056/events/0/events/0&quot;: &quot;/ir_semantics/ir_056/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_056/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_056/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_056/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_056/evidences&quot;,
      &quot;/ir_semantics/ir_056/events/0/evidences&quot;: &quot;/ir_semantics/ir_056/evidences&quot;,
      &quot;/ir_semantics/ir_057&quot;: &quot;/ir_semantics/ir_057&quot;,
      &quot;/ir_semantics/ir_058&quot;: &quot;/ir_semantics/ir_058&quot;,
      &quot;/ir_semantics/ir_058/events/0&quot;: &quot;/ir_semantics/ir_058/segments/0&quot;,
      &quot;/ir_semantics/ir_058/events/0/events/0&quot;: &quot;/ir_semantics/ir_058/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_058/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_058/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_058/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_058/evidences&quot;,
      &quot;/ir_semantics/ir_058/events/0/evidences&quot;: &quot;/ir_semantics/ir_058/evidences&quot;,
      &quot;/ir_semantics/ir_058/output_bindings/0&quot;: &quot;/ir_semantics/ir_058/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_058/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_058/evidences&quot;,
      &quot;/ir_semantics/ir_059&quot;: &quot;/ir_semantics/ir_059&quot;,
      &quot;/ir_semantics/ir_059/events/0&quot;: &quot;/ir_semantics/ir_059/segments/0&quot;,
      &quot;/ir_semantics/ir_059/events/0/events/0&quot;: &quot;/ir_semantics/ir_059/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_059/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_059/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_059/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_059/evidences&quot;,
      &quot;/ir_semantics/ir_059/events/0/events/1&quot;: &quot;/ir_semantics/ir_059/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_059/events/0/events/1/atomic_ops/0&quot;: &quot;/ir_semantics/ir_059/segments/0/ops/1&quot;,
      &quot;/ir_semantics/ir_059/events/0/events/1/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_059/evidences&quot;,
      &quot;/ir_semantics/ir_059/events/0/evidences&quot;: &quot;/ir_semantics/ir_059/evidences&quot;,
      &quot;/ir_semantics/ir_060&quot;: &quot;/ir_semantics/ir_060&quot;,
      &quot;/ir_semantics/ir_062&quot;: &quot;/ir_semantics/ir_062&quot;,
      &quot;/location_evidences/api_key_environment&quot;: &quot;/locations/api_key_environment/evidences&quot;,
      &quot;/location_evidences/cse_id_environment&quot;: &quot;/locations/cse_id_environment/evidences&quot;,
      &quot;/location_evidences/google_search_api&quot;: &quot;/locations/google_search_api/evidences&quot;,
      &quot;/location_evidences/stdout&quot;: &quot;/locations/stdout/evidences&quot;,
      &quot;/locations/api_key_environment&quot;: &quot;/locations/api_key_environment&quot;,
      &quot;/locations/cse_id_environment&quot;: &quot;/locations/cse_id_environment&quot;,
      &quot;/locations/google_search_api&quot;: &quot;/locations/google_search_api&quot;,
      &quot;/locations/stdout&quot;: &quot;/locations/stdout&quot;,
      &quot;/realizations/0&quot;: &quot;/realizations/0&quot;,
      &quot;/realizations/1&quot;: &quot;/realizations/1&quot;,
      &quot;/realizations/10&quot;: &quot;/realizations/10&quot;,
      &quot;/realizations/2&quot;: &quot;/realizations/2&quot;,
      &quot;/realizations/3&quot;: &quot;/realizations/3&quot;,
      &quot;/realizations/4&quot;: &quot;/realizations/4&quot;,
      &quot;/realizations/5&quot;: &quot;/realizations/5&quot;,
      &quot;/realizations/6&quot;: &quot;/realizations/6&quot;,
      &quot;/realizations/7&quot;: &quot;/realizations/7&quot;,
      &quot;/realizations/8&quot;: &quot;/realizations/8&quot;,
      &quot;/realizations/9&quot;: &quot;/realizations/9&quot;
    },
    &quot;wire_sha256&quot;: &quot;72fb208afb3d7d7caf77c3dc5412a93c8d5c8f682c31217bbae5c9b52320189d&quot;,
    &quot;wire_version&quot;: &quot;skillflow-flat-annotation-v7&quot;
  },
  &quot;raw_annotation&quot;: {
    &quot;demands&quot;: [
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;truth&quot;,
        &quot;reason&quot;: &quot;Credential validation depends on the received API key&#x27;s falsiness.&quot;,
        &quot;requirement_id&quot;: &quot;R6&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_042&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;truth&quot;,
        &quot;reason&quot;: &quot;Credential validation separately depends on the received engine ID&#x27;s falsiness.&quot;,
        &quot;requirement_id&quot;: &quot;R6&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 1,
          &quot;instruction_id&quot;: &quot;ir_042&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;action&quot;,
        &quot;reason&quot;: &quot;The missing-credential route must report its error and terminate unsuccessfully.&quot;,
        &quot;requirement_id&quot;: &quot;R6&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_043&quot;,
          &quot;path&quot;: []
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;value&quot;,
        &quot;reason&quot;: &quot;This literal is the specified missing-credentials report.&quot;,
        &quot;requirement_id&quot;: &quot;R6&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_043&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;expected&quot;: {
          &quot;kind&quot;: &quot;literal&quot;,
          &quot;value&quot;: 1
        },
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;value&quot;,
        &quot;reason&quot;: &quot;The missing-credential route uses unsuccessful exit status 1.&quot;,
        &quot;requirement_id&quot;: &quot;R6&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 3,
          &quot;instruction_id&quot;: &quot;ir_043&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;cardinality&quot;,
        &quot;reason&quot;: &quot;Argument cardinality determines whether a query argument exists.&quot;,
        &quot;requirement_id&quot;: &quot;R7&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 1,
          &quot;instruction_id&quot;: &quot;ir_026&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;action&quot;,
        &quot;reason&quot;: &quot;The missing-query route must display usage and terminate unsuccessfully.&quot;,
        &quot;requirement_id&quot;: &quot;R7&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_028&quot;,
          &quot;path&quot;: []
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;value&quot;,
        &quot;reason&quot;: &quot;The supplied usage literal describes the accepted command arguments.&quot;,
        &quot;requirement_id&quot;: &quot;R7&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_028&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;expected&quot;: {
          &quot;kind&quot;: &quot;literal&quot;,
          &quot;value&quot;: 1
        },
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;value&quot;,
        &quot;reason&quot;: &quot;The missing-query route uses unsuccessful exit status 1.&quot;,
        &quot;requirement_id&quot;: &quot;R7&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 3,
          &quot;instruction_id&quot;: &quot;ir_028&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;action&quot;,
        &quot;reason&quot;: &quot;A supplied second command-line argument is converted with int.&quot;,
        &quot;requirement_id&quot;: &quot;R8&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_032&quot;,
          &quot;path&quot;: []
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [
          2
        ],
        &quot;preserve&quot;: &quot;value&quot;,
        &quot;reason&quot;: &quot;Conversion must consume this argv snapshot&#x27;s actual count argument.&quot;,
        &quot;requirement_id&quot;: &quot;R8&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_032&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;expected&quot;: {
          &quot;kind&quot;: &quot;literal&quot;,
          &quot;value&quot;: 5
        },
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;value&quot;,
        &quot;reason&quot;: &quot;Omitting the count selects the specified default.&quot;,
        &quot;requirement_id&quot;: &quot;R8&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_035&quot;,
          &quot;side&quot;: &quot;output&quot;
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;value&quot;,
        &quot;reason&quot;: &quot;The runtime count must retain the value selected from the actual predecessor.&quot;,
        &quot;requirement_id&quot;: &quot;R8&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_037&quot;,
          &quot;side&quot;: &quot;output&quot;
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;value&quot;,
        &quot;reason&quot;: &quot;The helper receives the CLI&#x27;s actual query.&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 1,
          &quot;instruction_id&quot;: &quot;ir_045&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;value&quot;,
        &quot;reason&quot;: &quot;The helper receives the actual API-key environment value.&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 2,
          &quot;instruction_id&quot;: &quot;ir_045&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;value&quot;,
        &quot;reason&quot;: &quot;The helper receives the separate engine-ID environment value.&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 3,
          &quot;instruction_id&quot;: &quot;ir_045&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;value&quot;,
        &quot;reason&quot;: &quot;The helper receives the CLI-selected count explicitly.&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 4,
          &quot;instruction_id&quot;: &quot;ir_045&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;action&quot;,
        &quot;reason&quot;: &quot;The retrieved content must undergo JSON serialization for presentation.&quot;,
        &quot;requirement_id&quot;: &quot;R10&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_053&quot;,
          &quot;path&quot;: []
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;presence&quot;,
        &quot;reason&quot;: &quot;Serialization consumes the actual decoded helper return; no complete-response field necessity is asserted.&quot;,
        &quot;requirement_id&quot;: &quot;R10&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_053&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;presence&quot;,
        &quot;reason&quot;: &quot;The caller receives the actual helper return in its results binding.&quot;,
        &quot;requirement_id&quot;: &quot;R10&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_053&quot;,
          &quot;side&quot;: &quot;output&quot;
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;action&quot;,
        &quot;reason&quot;: &quot;The public response requires HTTP-status checking before decoding.&quot;,
        &quot;requirement_id&quot;: &quot;R11&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_010&quot;,
          &quot;path&quot;: []
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;action&quot;,
        &quot;reason&quot;: &quot;The CLI helper response requires HTTP-status checking before decoding.&quot;,
        &quot;requirement_id&quot;: &quot;R11&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_049&quot;,
          &quot;path&quot;: []
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;action&quot;,
        &quot;reason&quot;: &quot;A matching protected exception requires error reporting and unsuccessful termination.&quot;,
        &quot;requirement_id&quot;: &quot;R11&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_061&quot;,
          &quot;path&quot;: []
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;value&quot;,
        &quot;reason&quot;: &quot;The displayed error must contain the message obtained from the actual caught exception.&quot;,
        &quot;requirement_id&quot;: &quot;R11&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 1,
          &quot;instruction_id&quot;: &quot;ir_061&quot;,
          &quot;side&quot;: &quot;output&quot;
        }
      },
      {
        &quot;expected&quot;: {
          &quot;kind&quot;: &quot;literal&quot;,
          &quot;value&quot;: 1
        },
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;value&quot;,
        &quot;reason&quot;: &quot;Successful handler reporting is followed by exit status 1.&quot;,
        &quot;requirement_id&quot;: &quot;R11&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 6,
          &quot;instruction_id&quot;: &quot;ir_061&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      }
    ],
    &quot;expressions&quot;: [],
    &quot;ir_semantics&quot;: {
      &quot;ir_001&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;reason&quot;: &quot;Acquire the activation selector independently of invocation arguments.&quot;,
                &quot;target&quot;: {
                  &quot;instruction_id&quot;: &quot;ir_001&quot;,
                  &quot;path&quot;: []
                }
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;index&quot;: 0,
              &quot;kind&quot;: &quot;input&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_002&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 18,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 6
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 0,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;kind&quot;: &quot;value&quot;,
                    &quot;op&quot;: &quot;placeholder&quot;,
                    &quot;output&quot;: &quot;public_activation&quot;,
                    &quot;reason&quot;: &quot;The CFG supplies the activation alternatives but leaves the selector&#x27;s concrete representation unspecified.&quot;
                  }
                ],
                &quot;effect&quot;: null
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;reason&quot;: &quot;The CFG distinguishes public invocation from module evaluation; it does not specify a concrete selector encoding.&quot;,
                        &quot;target&quot;: {
                          &quot;instruction_id&quot;: &quot;ir_002&quot;,
                          &quot;path&quot;: []
                        }
                      }
                    ],
                    &quot;false_target&quot;: &quot;block_011&quot;,
                    &quot;input&quot;: {
                      &quot;kind&quot;: &quot;local&quot;,
                      &quot;name&quot;: &quot;public_activation&quot;
                    },
                    &quot;op&quot;: &quot;branch&quot;,
                    &quot;predicate&quot;: &quot;truthy&quot;,
                    &quot;true_target&quot;: &quot;block_002&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;reason&quot;: &quot;The CFG distinguishes public invocation from module evaluation; it does not specify a concrete selector encoding.&quot;,
                &quot;target&quot;: {
                  &quot;instruction_id&quot;: &quot;ir_002&quot;,
                  &quot;path&quot;: []
                }
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_003&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 6,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Bind each parameter to its own invocation input snapshot, preserving the optional count snapshot and the source-supported default 5 without replacing the entry snapshot with a computed default.&quot;,
                &quot;start_line&quot;: 6
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;index&quot;: 0,
              &quot;kind&quot;: &quot;input&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 6,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Bind each parameter to its own invocation input snapshot, preserving the optional count snapshot and the source-supported default 5 without replacing the entry snapshot with a computed default.&quot;,
                &quot;start_line&quot;: 6
              }
            ],
            &quot;output_index&quot;: 1,
            &quot;value&quot;: {
              &quot;index&quot;: 1,
              &quot;kind&quot;: &quot;input&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 6,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Bind each parameter to its own invocation input snapshot, preserving the optional count snapshot and the source-supported default 5 without replacing the entry snapshot with a computed default.&quot;,
                &quot;start_line&quot;: 6
              }
            ],
            &quot;output_index&quot;: 2,
            &quot;value&quot;: {
              &quot;index&quot;: 2,
              &quot;kind&quot;: &quot;input&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 6,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Bind each parameter to its own invocation input snapshot, preserving the optional count snapshot and the source-supported default 5 without replacing the entry snapshot with a computed default.&quot;,
                &quot;start_line&quot;: 6
              }
            ],
            &quot;output_index&quot;: 3,
            &quot;value&quot;: {
              &quot;index&quot;: 3,
              &quot;kind&quot;: &quot;input&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 19,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The Skill identifies the API key as a credential, supporting sensitivity of the entire credential field independently of its accesses.&quot;,
                &quot;start_line&quot;: 13
              },
              {
                &quot;end_line&quot;: 11,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;This invocation&#x27;s api_key parameter supplies the request&#x27;s key field; the declaration covers the original bound argument.&quot;,
                &quot;start_line&quot;: 6
              }
            ],
            &quot;label&quot;: &quot;API credential&quot;,
            &quot;path&quot;: [],
            &quot;property&quot;: &quot;value&quot;,
            &quot;source_access_id&quot;: &quot;access_a8a5938bc41ef8de647e7f3e&quot;,
            &quot;source_entry_applicability&quot;: &quot;source_field&quot;,
            &quot;source_entry_context&quot;: &quot;872bf9fd17c7a9c3fd3d359543a8a3564094ab68bdc8c622405bae727c9f0215&quot;,
            &quot;source_entry_id&quot;: &quot;entry_a99bc97f8d1f4a9dc277bff1&quot;,
            &quot;source_entry_location&quot;: &quot;runtime_context:google_search.invocation.bound.api_key&quot;,
            &quot;source_entry_origin&quot;: &quot;skill_argument&quot;,
            &quot;value&quot;: {
              &quot;index&quot;: 1,
              &quot;kind&quot;: &quot;input&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 19,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The Skill includes the CX ID among credentials, supporting sensitivity of the entire credential field independently of its accesses.&quot;,
                &quot;start_line&quot;: 14
              },
              {
                &quot;end_line&quot;: 11,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;This invocation&#x27;s cse_id parameter supplies the request&#x27;s cx field; the declaration covers the original bound argument.&quot;,
                &quot;start_line&quot;: 6
              }
            ],
            &quot;label&quot;: &quot;Search engine credential&quot;,
            &quot;path&quot;: [],
            &quot;property&quot;: &quot;value&quot;,
            &quot;source_access_id&quot;: &quot;access_2e977d982b523d2290dfea2c&quot;,
            &quot;source_entry_applicability&quot;: &quot;source_field&quot;,
            &quot;source_entry_context&quot;: &quot;872bf9fd17c7a9c3fd3d359543a8a3564094ab68bdc8c622405bae727c9f0215&quot;,
            &quot;source_entry_id&quot;: &quot;entry_25133a4ea1320fa498ba81cf&quot;,
            &quot;source_entry_location&quot;: &quot;runtime_context:google_search.invocation.bound.cse_id&quot;,
            &quot;source_entry_origin&quot;: &quot;skill_argument&quot;,
            &quot;value&quot;: {
              &quot;index&quot;: 2,
              &quot;kind&quot;: &quot;input&quot;
            }
          }
        ]
      },
      &quot;ir_004&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_005&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;container&quot;: &quot;object&quot;,
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 13,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 7
                      }
                    ],
                    &quot;op&quot;: &quot;build&quot;,
                    &quot;output&quot;: &quot;params&quot;,
                    &quot;parts&quot;: [
                      {
                        &quot;path&quot;: [
                          &quot;q&quot;
                        ],
                        &quot;value&quot;: {
                          &quot;index&quot;: 1,
                          &quot;kind&quot;: &quot;input&quot;
                        },
                        &quot;when&quot;: null
                      },
                      {
                        &quot;path&quot;: [
                          &quot;key&quot;
                        ],
                        &quot;value&quot;: {
                          &quot;index&quot;: 2,
                          &quot;kind&quot;: &quot;input&quot;
                        },
                        &quot;when&quot;: null
                      },
                      {
                        &quot;path&quot;: [
                          &quot;cx&quot;
                        ],
                        &quot;value&quot;: {
                          &quot;index&quot;: 3,
                          &quot;kind&quot;: &quot;input&quot;
                        },
                        &quot;when&quot;: null
                      },
                      {
                        &quot;path&quot;: [
                          &quot;num&quot;
                        ],
                        &quot;value&quot;: {
                          &quot;index&quot;: 4,
                          &quot;kind&quot;: &quot;input&quot;
                        },
                        &quot;when&quot;: null
                      }
                    ]
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 13,
                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                    &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                    &quot;start_line&quot;: 7
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 13,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 7
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 13,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 7
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;index&quot;: 0,
              &quot;kind&quot;: &quot;input&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 13,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 7
              }
            ],
            &quot;output_index&quot;: 1,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;params&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_006&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_007&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demands&quot;: [
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;action&quot;,
                        &quot;reason&quot;: &quot;Perform this public invocation&#x27;s remote search request.&quot;,
                        &quot;requirement_id&quot;: &quot;R9&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;self&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;The complete URL identifies the required Google Custom Search destination.&quot;,
                        &quot;requirement_id&quot;: &quot;R9&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 0,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [
                          &quot;q&quot;
                        ],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Forward this invocation&#x27;s query in its query role.&quot;,
                        &quot;requirement_id&quot;: &quot;R9&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 1,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [
                          &quot;key&quot;
                        ],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Forward this invocation&#x27;s API key in its credential role.&quot;,
                        &quot;requirement_id&quot;: &quot;R9&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 1,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [
                          &quot;cx&quot;
                        ],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Forward this invocation&#x27;s engine identifier in its engine-selection role.&quot;,
                        &quot;requirement_id&quot;: &quot;R9&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 1,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [
                          &quot;num&quot;
                        ],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Forward the requested count without asserting an unsupported remote range restriction.&quot;,
                        &quot;requirement_id&quot;: &quot;R9&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 1,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      }
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 14,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 14
                      }
                    ],
                    &quot;input_contract&quot;: {
                      &quot;evidences&quot;: [
                        {
                          &quot;end_line&quot;: 19,
                          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                          &quot;reason&quot;: &quot;The Skill describes search through Custom Search and requires API and CX credentials.&quot;,
                          &quot;start_line&quot;: 3
                        },
                        {
                          &quot;end_line&quot;: 14,
                          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                          &quot;reason&quot;: &quot;The callable maps query, key, engine and count into the actual request.&quot;,
                          &quot;start_line&quot;: 6
                        }
                      ],
                      &quot;inputs&quot;: [
                        {
                          &quot;input_index&quot;: 0,
                          &quot;reason&quot;: &quot;The complete URL identifies the actual HTTPS request destination.&quot;,
                          &quot;remainder&quot;: &quot;independent&quot;,
                          &quot;required&quot;: [
                            {
                              &quot;path&quot;: [],
                              &quot;property&quot;: &quot;value&quot;
                            }
                          ]
                        },
                        {
                          &quot;input_index&quot;: 1,
                          &quot;reason&quot;: &quot;The search query and the configured API and engine credentials are source-supported interface inputs. The count is preserved as actual payload without asserting unsupported API necessity.&quot;,
                          &quot;remainder&quot;: &quot;independent&quot;,
                          &quot;required&quot;: [
                            {
                              &quot;path&quot;: [
                                &quot;q&quot;
                              ],
                              &quot;property&quot;: &quot;value&quot;
                            },
                            {
                              &quot;path&quot;: [
                                &quot;key&quot;
                              ],
                              &quot;property&quot;: &quot;value&quot;
                            },
                            {
                              &quot;path&quot;: [
                                &quot;cx&quot;
                              ],
                              &quot;property&quot;: &quot;value&quot;
                            }
                          ],
                          &quot;unresolved_ranges&quot;: [
                            {
                              &quot;gap&quot;: {
                                &quot;code&quot;: &quot;missing_interface&quot;,
                                &quot;evidences&quot;: [
                                  {
                                    &quot;end_line&quot;: 14,
                                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                                    &quot;reason&quot;: &quot;The signature default and request construction show actual forwarding, not the remote interface&#x27;s necessity or bounds.&quot;,
                                    &quot;start_line&quot;: 6
                                  }
                                ],
                                &quot;missing&quot;: &quot;The endpoint&#x27;s count-parameter requirement and accepted domain.&quot;,
                                &quot;reason&quot;: &quot;The source forwards num but supplies no Google API contract proving whether this member is required, optional or constrained to a supported range.&quot;,
                                &quot;resolution&quot;: &quot;Supply the relevant API interface specification for num.&quot;
                              },
                              &quot;information&quot;: {
                                &quot;path&quot;: [
                                  &quot;num&quot;
                                ],
                                &quot;property&quot;: &quot;value&quot;
                              }
                            }
                          ]
                        }
                      ],
                      &quot;reason&quot;: &quot;Preserve the actual URL and constructed parameter object. Query and credential requirements are supported; count-interface details remain specifically unresolved.&quot;
                    },
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      },
                      {
                        &quot;index&quot;: 2,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;deliver&quot;,
                    &quot;request_id&quot;: &quot;f8b04abd14a0db74a6723fa4b031c7d2601059222fe218a618a2dd1f519d98f6&quot;,
                    &quot;target&quot;: &quot;google_search_api&quot;
                  }
                ],
                &quot;effect&quot;: &quot;net_send&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 14,
                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                    &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                    &quot;start_line&quot;: 14
                  }
                ]
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demands&quot;: [],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 14,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 14
                      }
                    ],
                    &quot;input_contract&quot;: {
                      &quot;evidences&quot;: [
                        {
                          &quot;end_line&quot;: 19,
                          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                          &quot;reason&quot;: &quot;The Skill describes search through Custom Search and requires API and CX credentials.&quot;,
                          &quot;start_line&quot;: 3
                        },
                        {
                          &quot;end_line&quot;: 14,
                          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                          &quot;reason&quot;: &quot;The callable maps query, key, engine and count into the actual request.&quot;,
                          &quot;start_line&quot;: 6
                        }
                      ],
                      &quot;inputs&quot;: [
                        {
                          &quot;input_index&quot;: 0,
                          &quot;reason&quot;: &quot;The complete URL identifies the actual HTTPS request destination.&quot;,
                          &quot;remainder&quot;: &quot;independent&quot;,
                          &quot;required&quot;: [
                            {
                              &quot;path&quot;: [],
                              &quot;property&quot;: &quot;value&quot;
                            }
                          ]
                        },
                        {
                          &quot;input_index&quot;: 1,
                          &quot;reason&quot;: &quot;The search query and the configured API and engine credentials are source-supported interface inputs. The count is preserved as actual payload without asserting unsupported API necessity.&quot;,
                          &quot;remainder&quot;: &quot;independent&quot;,
                          &quot;required&quot;: [
                            {
                              &quot;path&quot;: [
                                &quot;q&quot;
                              ],
                              &quot;property&quot;: &quot;value&quot;
                            },
                            {
                              &quot;path&quot;: [
                                &quot;key&quot;
                              ],
                              &quot;property&quot;: &quot;value&quot;
                            },
                            {
                              &quot;path&quot;: [
                                &quot;cx&quot;
                              ],
                              &quot;property&quot;: &quot;value&quot;
                            }
                          ],
                          &quot;unresolved_ranges&quot;: [
                            {
                              &quot;gap&quot;: {
                                &quot;code&quot;: &quot;missing_interface&quot;,
                                &quot;evidences&quot;: [
                                  {
                                    &quot;end_line&quot;: 14,
                                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                                    &quot;reason&quot;: &quot;The signature default and request construction show actual forwarding, not the remote interface&#x27;s necessity or bounds.&quot;,
                                    &quot;start_line&quot;: 6
                                  }
                                ],
                                &quot;missing&quot;: &quot;The endpoint&#x27;s count-parameter requirement and accepted domain.&quot;,
                                &quot;reason&quot;: &quot;The source forwards num but supplies no Google API contract proving whether this member is required, optional or constrained to a supported range.&quot;,
                                &quot;resolution&quot;: &quot;Supply the relevant API interface specification for num.&quot;
                              },
                              &quot;information&quot;: {
                                &quot;path&quot;: [
                                  &quot;num&quot;
                                ],
                                &quot;property&quot;: &quot;value&quot;
                              }
                            }
                          ]
                        }
                      ],
                      &quot;reason&quot;: &quot;Preserve the actual URL and constructed parameter object. Query and credential requirements are supported; count-interface details remain specifically unresolved.&quot;
                    },
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      },
                      {
                        &quot;index&quot;: 2,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;location&quot;: &quot;google_search_api&quot;,
                    &quot;op&quot;: &quot;receive&quot;,
                    &quot;output&quot;: &quot;response&quot;,
                    &quot;request_id&quot;: &quot;f8b04abd14a0db74a6723fa4b031c7d2601059222fe218a618a2dd1f519d98f6&quot;
                  }
                ],
                &quot;effect&quot;: &quot;net_receive&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 14,
                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                    &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                    &quot;start_line&quot;: 14
                  }
                ]
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 14,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 14
                      }
                    ],
                    &quot;inputs&quot;: [],
                    &quot;kind&quot;: &quot;value&quot;,
                    &quot;op&quot;: &quot;placeholder&quot;,
                    &quot;output&quot;: &quot;exception&quot;,
                    &quot;reason&quot;: &quot;The actual exception raised by this requests.get occurrence is available only on its exceptional continuation. No successful response is supplied there.&quot;
                  }
                ],
                &quot;effect&quot;: null
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 14,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 14
                      }
                    ],
                    &quot;inputs&quot;: [],
                    &quot;kind&quot;: &quot;value&quot;,
                    &quot;op&quot;: &quot;placeholder&quot;,
                    &quot;output&quot;: &quot;returned&quot;,
                    &quot;reason&quot;: &quot;Boolean normal-completion control for this request occurrence, not an additional Requests return value.&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 14
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 14
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;response&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 14
              }
            ],
            &quot;output_index&quot;: 1,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;exception&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 14
              }
            ],
            &quot;output_index&quot;: 2,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;returned&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_008&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 14,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 14
                      }
                    ],
                    &quot;false_target&quot;: &quot;block_005&quot;,
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;branch&quot;,
                    &quot;predicate&quot;: &quot;truthy&quot;,
                    &quot;true_target&quot;: &quot;block_006&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 14
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_009&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_011&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 15,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 15
                      }
                    ],
                    &quot;false_target&quot;: &quot;block_007&quot;,
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;branch&quot;,
                    &quot;predicate&quot;: &quot;truthy&quot;,
                    &quot;true_target&quot;: &quot;block_008&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 15,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 15
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_012&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_014&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 16,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 16
                      }
                    ],
                    &quot;false_target&quot;: &quot;block_010&quot;,
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;branch&quot;,
                    &quot;predicate&quot;: &quot;truthy&quot;,
                    &quot;true_target&quot;: &quot;block_009&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 16,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 16
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_015&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_016&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_017&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 1,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 1
                      }
                    ],
                    &quot;inputs&quot;: [],
                    &quot;kind&quot;: &quot;value&quot;,
                    &quot;op&quot;: &quot;placeholder&quot;,
                    &quot;output&quot;: &quot;sys_module&quot;,
                    &quot;reason&quot;: &quot;The import initializes the sys binding; module creation versus reuse is unspecified.&quot;
                  }
                ],
                &quot;effect&quot;: null
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 2,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 2
                      }
                    ],
                    &quot;inputs&quot;: [],
                    &quot;kind&quot;: &quot;value&quot;,
                    &quot;op&quot;: &quot;placeholder&quot;,
                    &quot;output&quot;: &quot;json_module&quot;,
                    &quot;reason&quot;: &quot;The import initializes the json binding; module creation versus reuse is unspecified.&quot;
                  }
                ],
                &quot;effect&quot;: null
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 3,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 3
                      }
                    ],
                    &quot;inputs&quot;: [],
                    &quot;kind&quot;: &quot;value&quot;,
                    &quot;op&quot;: &quot;placeholder&quot;,
                    &quot;output&quot;: &quot;requests_module&quot;,
                    &quot;reason&quot;: &quot;The import initializes the requests binding; module creation versus reuse is unspecified.&quot;
                  }
                ],
                &quot;effect&quot;: null
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 4,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 4
                      }
                    ],
                    &quot;inputs&quot;: [],
                    &quot;kind&quot;: &quot;value&quot;,
                    &quot;op&quot;: &quot;placeholder&quot;,
                    &quot;output&quot;: &quot;os_module&quot;,
                    &quot;reason&quot;: &quot;The import initializes the os binding; module creation versus reuse is unspecified.&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 4,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 1
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 4,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 1
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;sys_module&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 4,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 1
              }
            ],
            &quot;output_index&quot;: 1,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;json_module&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 4,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 1
              }
            ],
            &quot;output_index&quot;: 2,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;requests_module&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 4,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 1
              }
            ],
            &quot;output_index&quot;: 3,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;os_module&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_018&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_019&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 16,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 6
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 0,
                        &quot;kind&quot;: &quot;input&quot;
                      },
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;kind&quot;: &quot;value&quot;,
                    &quot;op&quot;: &quot;placeholder&quot;,
                    &quot;output&quot;: &quot;function&quot;,
                    &quot;reason&quot;: &quot;Define the callable with its imported requests binding and default count. The function-object constructor is outside the atomic vocabulary; its body does not execute here.&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 16,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 6
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 16,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 6
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;function&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_020&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_021&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 18,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Acquire the module-evaluation name snapshot.&quot;,
                &quot;start_line&quot;: 18
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;index&quot;: 0,
              &quot;kind&quot;: &quot;input&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_022&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;dependencies&quot;: [
                      &quot;possible&quot;,
                      &quot;possible&quot;
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 18,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 18
                      }
                    ],
                    &quot;expression&quot;: {
                      &quot;evidences&quot;: [
                        {
                          &quot;end_line&quot;: 18,
                          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                          &quot;start_line&quot;: 18
                        }
                      ],
                      &quot;expression&quot;: {
                        &quot;left&quot;: {
                          &quot;op&quot;: &quot;ref&quot;,
                          &quot;value&quot;: {
                            &quot;index&quot;: 0,
                            &quot;kind&quot;: &quot;input&quot;
                          }
                        },
                        &quot;op&quot;: &quot;eq&quot;,
                        &quot;right&quot;: {
                          &quot;op&quot;: &quot;ref&quot;,
                          &quot;value&quot;: {
                            &quot;index&quot;: 1,
                            &quot;kind&quot;: &quot;input&quot;
                          }
                        }
                      }
                    },
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 0,
                        &quot;kind&quot;: &quot;input&quot;
                      },
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;compute&quot;,
                    &quot;output&quot;: &quot;is_main&quot;
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 18,
                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                    &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                    &quot;start_line&quot;: 18
                  }
                ]
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 18,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 18
                      }
                    ],
                    &quot;false_target&quot;: &quot;block_014&quot;,
                    &quot;input&quot;: {
                      &quot;kind&quot;: &quot;local&quot;,
                      &quot;name&quot;: &quot;is_main&quot;
                    },
                    &quot;op&quot;: &quot;branch&quot;,
                    &quot;predicate&quot;: &quot;truthy&quot;,
                    &quot;true_target&quot;: &quot;block_015&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 18,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 18
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_023&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_024&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 24,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Acquire this execution&#x27;s argv snapshot, retaining the whole object separately from subsequent cardinality and element selections.&quot;,
                &quot;start_line&quot;: 19
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;index&quot;: 0,
              &quot;kind&quot;: &quot;input&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_025&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_027&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;dependencies&quot;: [
                      &quot;possible&quot;,
                      &quot;possible&quot;
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 21,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 19
                      }
                    ],
                    &quot;expression&quot;: {
                      &quot;evidences&quot;: [
                        {
                          &quot;end_line&quot;: 21,
                          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                          &quot;start_line&quot;: 19
                        }
                      ],
                      &quot;expression&quot;: {
                        &quot;left&quot;: {
                          &quot;op&quot;: &quot;ref&quot;,
                          &quot;value&quot;: {
                            &quot;index&quot;: 0,
                            &quot;kind&quot;: &quot;input&quot;
                          }
                        },
                        &quot;op&quot;: &quot;lt&quot;,
                        &quot;right&quot;: {
                          &quot;op&quot;: &quot;ref&quot;,
                          &quot;value&quot;: {
                            &quot;index&quot;: 1,
                            &quot;kind&quot;: &quot;input&quot;
                          }
                        }
                      }
                    },
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 0,
                        &quot;kind&quot;: &quot;input&quot;
                      },
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;compute&quot;,
                    &quot;output&quot;: &quot;too_few&quot;
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 21,
                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                    &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                    &quot;start_line&quot;: 19
                  }
                ]
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 21,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 19
                      }
                    ],
                    &quot;false_target&quot;: &quot;block_018&quot;,
                    &quot;input&quot;: {
                      &quot;kind&quot;: &quot;local&quot;,
                      &quot;name&quot;: &quot;too_few&quot;
                    },
                    &quot;op&quot;: &quot;branch&quot;,
                    &quot;predicate&quot;: &quot;truthy&quot;,
                    &quot;true_target&quot;: &quot;block_017&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 21,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 19
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_029&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_030&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demands&quot;: [
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;The accepted query is the actual first command-line argument.&quot;,
                        &quot;requirement_id&quot;: &quot;R7&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;output&quot;
                        }
                      }
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 23,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 23
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;query&quot;,
                    &quot;path&quot;: [
                      1
                    ]
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 23,
                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                    &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                    &quot;start_line&quot;: 23
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 23,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 23
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 23,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 23
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;query&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_031&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;dependencies&quot;: [
                      &quot;possible&quot;,
                      &quot;possible&quot;
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 24,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 24
                      }
                    ],
                    &quot;expression&quot;: {
                      &quot;evidences&quot;: [
                        {
                          &quot;end_line&quot;: 24,
                          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                          &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                          &quot;start_line&quot;: 24
                        }
                      ],
                      &quot;expression&quot;: {
                        &quot;left&quot;: {
                          &quot;op&quot;: &quot;ref&quot;,
                          &quot;value&quot;: {
                            &quot;index&quot;: 0,
                            &quot;kind&quot;: &quot;input&quot;
                          }
                        },
                        &quot;op&quot;: &quot;gt&quot;,
                        &quot;right&quot;: {
                          &quot;op&quot;: &quot;ref&quot;,
                          &quot;value&quot;: {
                            &quot;index&quot;: 1,
                            &quot;kind&quot;: &quot;input&quot;
                          }
                        }
                      }
                    },
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 0,
                        &quot;kind&quot;: &quot;input&quot;
                      },
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;compute&quot;,
                    &quot;output&quot;: &quot;has_count&quot;
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 24,
                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                    &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                    &quot;start_line&quot;: 24
                  }
                ]
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 24,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 24
                      }
                    ],
                    &quot;false_target&quot;: &quot;block_021&quot;,
                    &quot;input&quot;: {
                      &quot;kind&quot;: &quot;local&quot;,
                      &quot;name&quot;: &quot;has_count&quot;
                    },
                    &quot;op&quot;: &quot;branch&quot;,
                    &quot;predicate&quot;: &quot;truthy&quot;,
                    &quot;true_target&quot;: &quot;block_019&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 24,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 24
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_033&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 24,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 24
                      }
                    ],
                    &quot;false_target&quot;: &quot;block_020&quot;,
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;branch&quot;,
                    &quot;predicate&quot;: &quot;truthy&quot;,
                    &quot;true_target&quot;: &quot;block_022&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 24,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 24
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_034&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_035&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 24,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 24
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;index&quot;: 0,
              &quot;kind&quot;: &quot;input&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_036&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_037&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 24,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 24
                      }
                    ],
                    &quot;incoming&quot;: [
                      {
                        &quot;predecessor&quot;: &quot;block_019&quot;,
                        &quot;value&quot;: {
                          &quot;index&quot;: 0,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      },
                      {
                        &quot;predecessor&quot;: &quot;block_021&quot;,
                        &quot;value&quot;: {
                          &quot;index&quot;: 1,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      }
                    ],
                    &quot;op&quot;: &quot;merge&quot;,
                    &quot;output&quot;: &quot;count&quot;
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 24,
                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                    &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                    &quot;start_line&quot;: 24
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 24,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 24
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 24,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 24
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;count&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_038&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_039&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demands&quot;: [
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;action&quot;,
                        &quot;reason&quot;: &quot;Acquire the runtime API key from its specifically named process-environment entry.&quot;,
                        &quot;requirement_id&quot;: &quot;R6&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;self&quot;
                        }
                      }
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 27,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;The explicitly keyed getenv interface reads this process-environment entry, not a demonstrated .env file read.&quot;,
                        &quot;start_line&quot;: 27
                      }
                    ],
                    &quot;location&quot;: &quot;api_key_environment&quot;,
                    &quot;op&quot;: &quot;read&quot;,
                    &quot;output&quot;: &quot;api_key&quot;
                  }
                ],
                &quot;effect&quot;: &quot;context_read&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 27,
                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                    &quot;reason&quot;: &quot;The explicitly keyed getenv interface reads this process-environment entry, not a demonstrated .env file read.&quot;,
                    &quot;start_line&quot;: 27
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 27,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;The explicitly keyed getenv interface reads this process-environment entry, not a demonstrated .env file read.&quot;,
                &quot;start_line&quot;: 27
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 27,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;The explicitly keyed getenv interface reads this process-environment entry, not a demonstrated .env file read.&quot;,
                &quot;start_line&quot;: 27
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;api_key&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 19,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;GOOGLE_API_KEY is explicitly a credential field, supporting source-field sensitivity for its entire value.&quot;,
                &quot;start_line&quot;: 15
              },
              {
                &quot;end_line&quot;: 27,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;The actual acquired version comes from this process-environment lookup. No file-loading relation establishes provenance from the documented .env file.&quot;,
                &quot;start_line&quot;: 26
              }
            ],
            &quot;label&quot;: &quot;API credential&quot;,
            &quot;path&quot;: [],
            &quot;property&quot;: &quot;value&quot;,
            &quot;source_access_id&quot;: &quot;access_02eac5d7fb9ef009c7f6cd23&quot;,
            &quot;source_entry_applicability&quot;: &quot;source_field&quot;,
            &quot;source_entry_context&quot;: &quot;c8590c2d815ca1e960b0af3a40643fdf9ec2cbcc50e6fab8c5893264edd6cf73&quot;,
            &quot;source_entry_id&quot;: &quot;entry_b7138bdfae3b0a77c4db6678&quot;,
            &quot;source_entry_location&quot;: &quot;runtime_context:process environment: GOOGLE_API_KEY&quot;,
            &quot;source_entry_origin&quot;: &quot;environment&quot;,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;api_key&quot;
            }
          }
        ]
      },
      &quot;ir_040&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_041&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demands&quot;: [
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;action&quot;,
                        &quot;reason&quot;: &quot;Acquire the runtime engine ID from its separate named process-environment entry.&quot;,
                        &quot;requirement_id&quot;: &quot;R6&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;self&quot;
                        }
                      }
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 28,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;The explicitly keyed getenv interface reads this separate process-environment entry.&quot;,
                        &quot;start_line&quot;: 28
                      }
                    ],
                    &quot;location&quot;: &quot;cse_id_environment&quot;,
                    &quot;op&quot;: &quot;read&quot;,
                    &quot;output&quot;: &quot;cse_id&quot;
                  }
                ],
                &quot;effect&quot;: &quot;context_read&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 28,
                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                    &quot;reason&quot;: &quot;The explicitly keyed getenv interface reads this separate process-environment entry.&quot;,
                    &quot;start_line&quot;: 28
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 28,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;The explicitly keyed getenv interface reads this separate process-environment entry.&quot;,
                &quot;start_line&quot;: 28
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 28,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;The explicitly keyed getenv interface reads this separate process-environment entry.&quot;,
                &quot;start_line&quot;: 28
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;cse_id&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 19,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;GOOGLE_CSE_ID is explicitly included among credentials, supporting source-field sensitivity for its entire value.&quot;,
                &quot;start_line&quot;: 15
              },
              {
                &quot;end_line&quot;: 28,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;The actual acquired version comes from the separate GOOGLE_CSE_ID process-environment lookup. No file-loading relation establishes provenance from the documented .env file.&quot;,
                &quot;start_line&quot;: 26
              }
            ],
            &quot;label&quot;: &quot;Search engine credential&quot;,
            &quot;path&quot;: [],
            &quot;property&quot;: &quot;value&quot;,
            &quot;source_access_id&quot;: &quot;access_0f610e2f135bb26640bbd4ef&quot;,
            &quot;source_entry_applicability&quot;: &quot;source_field&quot;,
            &quot;source_entry_context&quot;: &quot;c8590c2d815ca1e960b0af3a40643fdf9ec2cbcc50e6fab8c5893264edd6cf73&quot;,
            &quot;source_entry_id&quot;: &quot;entry_a2d3ccf4ddac9ffec2fcae8b&quot;,
            &quot;source_entry_location&quot;: &quot;runtime_context:process environment: GOOGLE_CSE_ID&quot;,
            &quot;source_entry_origin&quot;: &quot;environment&quot;,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;cse_id&quot;
            }
          }
        ]
      },
      &quot;ir_042&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demand_transfer&quot;: {
                      &quot;rules&quot;: [
                        {
                          &quot;evidences&quot;: [
                            {
                              &quot;end_line&quot;: 30,
                              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                              &quot;reason&quot;: &quot;The condition tests credential falsiness, without forwarding credential contents.&quot;,
                              &quot;start_line&quot;: 30
                            }
                          ],
                          &quot;inputs&quot;: [
                            {
                              &quot;input_index&quot;: 0,
                              &quot;reason&quot;: &quot;The first credential&#x27;s truth value determines its negated condition; its other information cannot change that Boolean.&quot;,
                              &quot;remainder&quot;: &quot;independent&quot;,
                              &quot;required&quot;: [
                                {
                                  &quot;path&quot;: [],
                                  &quot;property&quot;: &quot;truth&quot;
                                }
                              ]
                            },
                            {
                              &quot;input_index&quot;: 1,
                              &quot;reason&quot;: &quot;The second credential&#x27;s truth value determines its negated condition; its other information cannot change that Boolean.&quot;,
                              &quot;remainder&quot;: &quot;independent&quot;,
                              &quot;required&quot;: [
                                {
                                  &quot;path&quot;: [],
                                  &quot;property&quot;: &quot;truth&quot;
                                }
                              ]
                            }
                          ],
                          &quot;output&quot;: {
                            &quot;path&quot;: [],
                            &quot;property&quot;: &quot;value&quot;
                          },
                          &quot;reason&quot;: &quot;The disjunction of the two negated truth values suffices for the source condition.&quot;
                        }
                      ]
                    },
                    &quot;dependencies&quot;: [
                      &quot;possible&quot;,
                      &quot;possible&quot;
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 30,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 30
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 0,
                        &quot;kind&quot;: &quot;input&quot;
                      },
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;compute&quot;,
                    &quot;output&quot;: &quot;missing_credentials&quot;
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 30,
                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                    &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                    &quot;start_line&quot;: 30
                  }
                ]
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 30,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 30
                      }
                    ],
                    &quot;false_target&quot;: &quot;block_026&quot;,
                    &quot;input&quot;: {
                      &quot;kind&quot;: &quot;local&quot;,
                      &quot;name&quot;: &quot;missing_credentials&quot;
                    },
                    &quot;op&quot;: &quot;branch&quot;,
                    &quot;predicate&quot;: &quot;truthy&quot;,
                    &quot;true_target&quot;: &quot;block_025&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 30,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 30
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_044&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_046&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_047&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demands&quot;: [
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;action&quot;,
                        &quot;reason&quot;: &quot;Perform this CLI helper invocation&#x27;s remote search request.&quot;,
                        &quot;requirement_id&quot;: &quot;R9&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;self&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;The complete URL identifies the required Google Custom Search destination.&quot;,
                        &quot;requirement_id&quot;: &quot;R9&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 0,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [
                          &quot;q&quot;
                        ],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Send the query bound from this CLI invocation.&quot;,
                        &quot;requirement_id&quot;: &quot;R9&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 1,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [
                          &quot;key&quot;
                        ],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Send the API key bound from this execution&#x27;s environment read.&quot;,
                        &quot;requirement_id&quot;: &quot;R9&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 1,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [
                          &quot;cx&quot;
                        ],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Send the engine ID bound from its separate environment read.&quot;,
                        &quot;requirement_id&quot;: &quot;R9&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 1,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [
                          &quot;num&quot;
                        ],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Send this invocation&#x27;s selected result count in its prescribed parameter role.&quot;,
                        &quot;requirement_id&quot;: &quot;R9&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 1,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      }
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 14,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 14
                      }
                    ],
                    &quot;input_contract&quot;: {
                      &quot;evidences&quot;: [
                        {
                          &quot;end_line&quot;: 19,
                          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                          &quot;reason&quot;: &quot;The Skill describes search through Custom Search and requires API and CX credentials.&quot;,
                          &quot;start_line&quot;: 3
                        },
                        {
                          &quot;end_line&quot;: 14,
                          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                          &quot;reason&quot;: &quot;The callable maps query, key, engine and count into the actual request.&quot;,
                          &quot;start_line&quot;: 6
                        }
                      ],
                      &quot;inputs&quot;: [
                        {
                          &quot;input_index&quot;: 0,
                          &quot;reason&quot;: &quot;The complete URL identifies the actual HTTPS request destination.&quot;,
                          &quot;remainder&quot;: &quot;independent&quot;,
                          &quot;required&quot;: [
                            {
                              &quot;path&quot;: [],
                              &quot;property&quot;: &quot;value&quot;
                            }
                          ]
                        },
                        {
                          &quot;input_index&quot;: 1,
                          &quot;reason&quot;: &quot;The search query and the configured API and engine credentials are source-supported interface inputs. The count is preserved as actual payload without asserting unsupported API necessity.&quot;,
                          &quot;remainder&quot;: &quot;independent&quot;,
                          &quot;required&quot;: [
                            {
                              &quot;path&quot;: [
                                &quot;q&quot;
                              ],
                              &quot;property&quot;: &quot;value&quot;
                            },
                            {
                              &quot;path&quot;: [
                                &quot;key&quot;
                              ],
                              &quot;property&quot;: &quot;value&quot;
                            },
                            {
                              &quot;path&quot;: [
                                &quot;cx&quot;
                              ],
                              &quot;property&quot;: &quot;value&quot;
                            }
                          ],
                          &quot;unresolved_ranges&quot;: [
                            {
                              &quot;gap&quot;: {
                                &quot;code&quot;: &quot;missing_interface&quot;,
                                &quot;evidences&quot;: [
                                  {
                                    &quot;end_line&quot;: 14,
                                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                                    &quot;reason&quot;: &quot;The signature default and request construction show actual forwarding, not the remote interface&#x27;s necessity or bounds.&quot;,
                                    &quot;start_line&quot;: 6
                                  }
                                ],
                                &quot;missing&quot;: &quot;The endpoint&#x27;s count-parameter requirement and accepted domain.&quot;,
                                &quot;reason&quot;: &quot;The source forwards num but supplies no Google API contract proving whether this member is required, optional or constrained to a supported range.&quot;,
                                &quot;resolution&quot;: &quot;Supply the relevant API interface specification for num.&quot;
                              },
                              &quot;information&quot;: {
                                &quot;path&quot;: [
                                  &quot;num&quot;
                                ],
                                &quot;property&quot;: &quot;value&quot;
                              }
                            }
                          ]
                        }
                      ],
                      &quot;reason&quot;: &quot;Preserve the actual URL and constructed parameter object. Query and credential requirements are supported; count-interface details remain specifically unresolved.&quot;
                    },
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      },
                      {
                        &quot;index&quot;: 2,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;deliver&quot;,
                    &quot;request_id&quot;: &quot;49b20321477c90cdbeec13c61dcc4ad4d6b4dbfbd1ee79f0e26f1968bcb98c63&quot;,
                    &quot;target&quot;: &quot;google_search_api&quot;
                  }
                ],
                &quot;effect&quot;: &quot;net_send&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 14,
                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                    &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                    &quot;start_line&quot;: 14
                  }
                ]
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demands&quot;: [],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 14,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 14
                      }
                    ],
                    &quot;input_contract&quot;: {
                      &quot;evidences&quot;: [
                        {
                          &quot;end_line&quot;: 19,
                          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                          &quot;reason&quot;: &quot;The Skill describes search through Custom Search and requires API and CX credentials.&quot;,
                          &quot;start_line&quot;: 3
                        },
                        {
                          &quot;end_line&quot;: 14,
                          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                          &quot;reason&quot;: &quot;The callable maps query, key, engine and count into the actual request.&quot;,
                          &quot;start_line&quot;: 6
                        }
                      ],
                      &quot;inputs&quot;: [
                        {
                          &quot;input_index&quot;: 0,
                          &quot;reason&quot;: &quot;The complete URL identifies the actual HTTPS request destination.&quot;,
                          &quot;remainder&quot;: &quot;independent&quot;,
                          &quot;required&quot;: [
                            {
                              &quot;path&quot;: [],
                              &quot;property&quot;: &quot;value&quot;
                            }
                          ]
                        },
                        {
                          &quot;input_index&quot;: 1,
                          &quot;reason&quot;: &quot;The search query and the configured API and engine credentials are source-supported interface inputs. The count is preserved as actual payload without asserting unsupported API necessity.&quot;,
                          &quot;remainder&quot;: &quot;independent&quot;,
                          &quot;required&quot;: [
                            {
                              &quot;path&quot;: [
                                &quot;q&quot;
                              ],
                              &quot;property&quot;: &quot;value&quot;
                            },
                            {
                              &quot;path&quot;: [
                                &quot;key&quot;
                              ],
                              &quot;property&quot;: &quot;value&quot;
                            },
                            {
                              &quot;path&quot;: [
                                &quot;cx&quot;
                              ],
                              &quot;property&quot;: &quot;value&quot;
                            }
                          ],
                          &quot;unresolved_ranges&quot;: [
                            {
                              &quot;gap&quot;: {
                                &quot;code&quot;: &quot;missing_interface&quot;,
                                &quot;evidences&quot;: [
                                  {
                                    &quot;end_line&quot;: 14,
                                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                                    &quot;reason&quot;: &quot;The signature default and request construction show actual forwarding, not the remote interface&#x27;s necessity or bounds.&quot;,
                                    &quot;start_line&quot;: 6
                                  }
                                ],
                                &quot;missing&quot;: &quot;The endpoint&#x27;s count-parameter requirement and accepted domain.&quot;,
                                &quot;reason&quot;: &quot;The source forwards num but supplies no Google API contract proving whether this member is required, optional or constrained to a supported range.&quot;,
                                &quot;resolution&quot;: &quot;Supply the relevant API interface specification for num.&quot;
                              },
                              &quot;information&quot;: {
                                &quot;path&quot;: [
                                  &quot;num&quot;
                                ],
                                &quot;property&quot;: &quot;value&quot;
                              }
                            }
                          ]
                        }
                      ],
                      &quot;reason&quot;: &quot;Preserve the actual URL and constructed parameter object. Query and credential requirements are supported; count-interface details remain specifically unresolved.&quot;
                    },
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      },
                      {
                        &quot;index&quot;: 2,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;location&quot;: &quot;google_search_api&quot;,
                    &quot;op&quot;: &quot;receive&quot;,
                    &quot;output&quot;: &quot;response&quot;,
                    &quot;request_id&quot;: &quot;49b20321477c90cdbeec13c61dcc4ad4d6b4dbfbd1ee79f0e26f1968bcb98c63&quot;
                  }
                ],
                &quot;effect&quot;: &quot;net_receive&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 14,
                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                    &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                    &quot;start_line&quot;: 14
                  }
                ]
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 14,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 14
                      }
                    ],
                    &quot;inputs&quot;: [],
                    &quot;kind&quot;: &quot;value&quot;,
                    &quot;op&quot;: &quot;placeholder&quot;,
                    &quot;output&quot;: &quot;exception&quot;,
                    &quot;reason&quot;: &quot;The actual exception raised by this requests.get occurrence is available only on its exceptional continuation. No successful response is supplied there.&quot;
                  }
                ],
                &quot;effect&quot;: null
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 14,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 14
                      }
                    ],
                    &quot;inputs&quot;: [],
                    &quot;kind&quot;: &quot;value&quot;,
                    &quot;op&quot;: &quot;placeholder&quot;,
                    &quot;output&quot;: &quot;returned&quot;,
                    &quot;reason&quot;: &quot;Boolean normal-completion control for this request occurrence, not an additional Requests return value.&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 14
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 14
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;response&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 14
              }
            ],
            &quot;output_index&quot;: 1,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;exception&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 14
              }
            ],
            &quot;output_index&quot;: 2,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;returned&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_048&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 14,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 14
                      }
                    ],
                    &quot;false_target&quot;: &quot;block_033&quot;,
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;branch&quot;,
                    &quot;predicate&quot;: &quot;truthy&quot;,
                    &quot;true_target&quot;: &quot;block_028&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 14
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_050&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 15,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 15
                      }
                    ],
                    &quot;false_target&quot;: &quot;block_033&quot;,
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;branch&quot;,
                    &quot;predicate&quot;: &quot;truthy&quot;,
                    &quot;true_target&quot;: &quot;block_029&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 15,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 15
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_052&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 16,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 16
                      }
                    ],
                    &quot;false_target&quot;: &quot;block_033&quot;,
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;branch&quot;,
                    &quot;predicate&quot;: &quot;truthy&quot;,
                    &quot;true_target&quot;: &quot;block_030&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 16,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 16
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_054&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 36,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 36
                      }
                    ],
                    &quot;false_target&quot;: &quot;block_033&quot;,
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;branch&quot;,
                    &quot;predicate&quot;: &quot;truthy&quot;,
                    &quot;true_target&quot;: &quot;block_031&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 36,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 36
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_055&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demands&quot;: [
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;action&quot;,
                        &quot;reason&quot;: &quot;Deliver the JSON presentation to the actual stdout recipient.&quot;,
                        &quot;requirement_id&quot;: &quot;R10&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;self&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;presence&quot;,
                        &quot;reason&quot;: &quot;The delivery consumes the formatted JSON payload, distinct from the decoded object and request parameters; exact formatting and every response member are not independently required.&quot;,
                        &quot;requirement_id&quot;: &quot;R10&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 0,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      }
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 36,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 36
                      }
                    ],
                    &quot;input_contract&quot;: {
                      &quot;evidences&quot;: [
                        {
                          &quot;end_line&quot;: 38,
                          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                          &quot;reason&quot;: &quot;Usage, credential errors, formatted JSON and caught-error messages are delivered through print.&quot;,
                          &quot;start_line&quot;: 20
                        }
                      ],
                      &quot;inputs&quot;: [
                        {
                          &quot;input_index&quot;: 0,
                          &quot;reason&quot;: &quot;Delivering this exact selected output string requires its complete value; this is a delivery-interface obligation, not a claim that every originating result field is required by the task.&quot;,
                          &quot;remainder&quot;: &quot;independent&quot;,
                          &quot;required&quot;: [
                            {
                              &quot;path&quot;: [],
                              &quot;property&quot;: &quot;value&quot;
                            }
                          ]
                        }
                      ],
                      &quot;reason&quot;: &quot;The print sites supply one selected string to stdout. The stream&#x27;s subsequent routing is not specified.&quot;
                    },
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;deliver&quot;,
                    &quot;target&quot;: &quot;stdout&quot;
                  }
                ],
                &quot;effect&quot;: null
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 36,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 36
                      }
                    ],
                    &quot;inputs&quot;: [],
                    &quot;kind&quot;: &quot;value&quot;,
                    &quot;op&quot;: &quot;placeholder&quot;,
                    &quot;output&quot;: &quot;exception&quot;,
                    &quot;reason&quot;: &quot;The actual exception from this print invocation; output may already be partial, with no source-supported rollback.&quot;
                  }
                ],
                &quot;effect&quot;: null
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 36,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 36
                      }
                    ],
                    &quot;inputs&quot;: [],
                    &quot;kind&quot;: &quot;value&quot;,
                    &quot;op&quot;: &quot;placeholder&quot;,
                    &quot;output&quot;: &quot;returned&quot;,
                    &quot;reason&quot;: &quot;Boolean normal-completion control for this print, whose ordinary return is discarded.&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 36,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 36
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 36,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 36
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;exception&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 36,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 36
              }
            ],
            &quot;output_index&quot;: 1,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;returned&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_056&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 36,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 36
                      }
                    ],
                    &quot;false_target&quot;: &quot;block_033&quot;,
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;branch&quot;,
                    &quot;predicate&quot;: &quot;truthy&quot;,
                    &quot;true_target&quot;: &quot;block_032&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 36,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 36
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_057&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_058&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 37,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 37
                      }
                    ],
                    &quot;incoming&quot;: [
                      {
                        &quot;predecessor&quot;: &quot;block_027&quot;,
                        &quot;value&quot;: {
                          &quot;index&quot;: 0,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      },
                      {
                        &quot;predecessor&quot;: &quot;block_028&quot;,
                        &quot;value&quot;: {
                          &quot;index&quot;: 1,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      },
                      {
                        &quot;predecessor&quot;: &quot;block_029&quot;,
                        &quot;value&quot;: {
                          &quot;index&quot;: 2,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      },
                      {
                        &quot;predecessor&quot;: &quot;block_030&quot;,
                        &quot;value&quot;: {
                          &quot;index&quot;: 3,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      },
                      {
                        &quot;predecessor&quot;: &quot;block_031&quot;,
                        &quot;value&quot;: {
                          &quot;index&quot;: 4,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      }
                    ],
                    &quot;op&quot;: &quot;merge&quot;,
                    &quot;output&quot;: &quot;raised&quot;
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 37,
                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                    &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                    &quot;start_line&quot;: 37
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 37,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 37
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 37,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 37
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;raised&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_059&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demand_transfer&quot;: {
                      &quot;rules&quot;: [
                        {
                          &quot;evidences&quot;: [
                            {
                              &quot;end_line&quot;: 37,
                              &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                              &quot;reason&quot;: &quot;Only matching exceptions enter this handler.&quot;,
                              &quot;start_line&quot;: 37
                            }
                          ],
                          &quot;inputs&quot;: [
                            {
                              &quot;gap&quot;: {
                                &quot;code&quot;: &quot;unsupported_relation&quot;,
                                &quot;evidences&quot;: [
                                  {
                                    &quot;end_line&quot;: 37,
                                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                                    &quot;reason&quot;: &quot;except Exception performs class-based matching, not a textual or JSON-field test.&quot;,
                                    &quot;start_line&quot;: 37
                                  }
                                ],
                                &quot;missing&quot;: &quot;A representation of the actual raised value&#x27;s membership in Exception.&quot;,
                                &quot;reason&quot;: &quot;The available typed expression language has no exception-class inheritance test and the source supplies no scalar class tag to select.&quot;,
                                &quot;resolution&quot;: &quot;Supply a supported exception-type predicate or an evidenced class tag and inheritance relation.&quot;
                              },
                              &quot;input_index&quot;: 0,
                              &quot;reason&quot;: &quot;Handler membership depends on the actual raised value&#x27;s exception class, whose representation is not exposed.&quot;,
                              &quot;remainder&quot;: &quot;unresolved&quot;,
                              &quot;required&quot;: []
                            }
                          ],
                          &quot;output&quot;: {
                            &quot;path&quot;: [],
                            &quot;property&quot;: &quot;value&quot;
                          },
                          &quot;reason&quot;: &quot;Retain the source-supported handler-matching Boolean and both CFG continuations while keeping its representation limitation local.&quot;
                        }
                      ]
                    },
                    &quot;dependencies&quot;: [
                      &quot;possible&quot;
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 37,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 37
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 0,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;compute&quot;,
                    &quot;output&quot;: &quot;matches_exception&quot;
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 37,
                    &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                    &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                    &quot;start_line&quot;: 37
                  }
                ]
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 37,
                        &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                        &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                        &quot;start_line&quot;: 37
                      }
                    ],
                    &quot;false_target&quot;: &quot;block_034&quot;,
                    &quot;input&quot;: {
                      &quot;kind&quot;: &quot;local&quot;,
                      &quot;name&quot;: &quot;matches_exception&quot;
                    },
                    &quot;op&quot;: &quot;branch&quot;,
                    &quot;predicate&quot;: &quot;truthy&quot;,
                    &quot;true_target&quot;: &quot;block_035&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 37,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 37
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_060&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_062&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      }
    },
    &quot;location_evidences&quot;: {
      &quot;api_key_environment&quot;: [
        {
          &quot;end_line&quot;: 27,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;The literal getenv key identifies this entry within process environment state.&quot;,
          &quot;start_line&quot;: 27
        },
        {
          &quot;reason&quot;: &quot;Runtime context defaults to task access and task retention.&quot;,
          &quot;rule_id&quot;: &quot;EM12&quot;
        }
      ],
      &quot;cse_id_environment&quot;: [
        {
          &quot;end_line&quot;: 28,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;The literal getenv key identifies this separate entry within process environment state.&quot;,
          &quot;start_line&quot;: 28
        },
        {
          &quot;reason&quot;: &quot;Runtime context defaults to task access and task retention.&quot;,
          &quot;rule_id&quot;: &quot;EM12&quot;
        }
      ],
      &quot;google_search_api&quot;: [
        {
          &quot;end_line&quot;: 14,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;The HTTPS URL and requests.get establish network transport to this endpoint.&quot;,
          &quot;start_line&quot;: 7
        },
        {
          &quot;reason&quot;: &quot;Remote access defaults to recipient scope; backend retention is not established.&quot;,
          &quot;rule_id&quot;: &quot;EM12&quot;
        }
      ],
      &quot;stdout&quot;: [
        {
          &quot;end_line&quot;: 38,
          &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
          &quot;reason&quot;: &quot;print delivers the selected strings to process stdout. Its downstream consumer is unspecified.&quot;,
          &quot;start_line&quot;: 20
        },
        {
          &quot;reason&quot;: &quot;A process output stream does not establish network transport, human-facing output or model observation.&quot;,
          &quot;rule_id&quot;: &quot;EM06&quot;
        },
        {
          &quot;reason&quot;: &quot;Unspecified receiving deployment retains a recipient possibility; persistence is not established.&quot;,
          &quot;rule_id&quot;: &quot;EM12&quot;
        }
      ]
    },
    &quot;locations&quot;: {
      &quot;api_key_environment&quot;: {
        &quot;access_scope&quot;: &quot;task&quot;,
        &quot;kind&quot;: &quot;runtime_context&quot;,
        &quot;name&quot;: &quot;process environment: GOOGLE_API_KEY&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 1,
            &quot;instruction_id&quot;: &quot;ir_039&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: &quot;task&quot;
      },
      &quot;cse_id_environment&quot;: {
        &quot;access_scope&quot;: &quot;task&quot;,
        &quot;kind&quot;: &quot;runtime_context&quot;,
        &quot;name&quot;: &quot;process environment: GOOGLE_CSE_ID&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 1,
            &quot;instruction_id&quot;: &quot;ir_041&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: &quot;task&quot;
      },
      &quot;google_search_api&quot;: {
        &quot;access_scope&quot;: &quot;recipient&quot;,
        &quot;kind&quot;: &quot;remote&quot;,
        &quot;name&quot;: &quot;https://www.googleapis.com/customsearch/v1&quot;,
        &quot;operand_refs&quot;: [],
        &quot;retention&quot;: null
      },
      &quot;stdout&quot;: {
        &quot;access_scope&quot;: &quot;recipient&quot;,
        &quot;kind&quot;: &quot;tool&quot;,
        &quot;name&quot;: &quot;process stdout&quot;,
        &quot;operand_refs&quot;: [],
        &quot;retention&quot;: null
      }
    },
    &quot;outcome&quot;: &quot;completed&quot;,
    &quot;processing_gaps&quot;: [
      {
        &quot;control&quot;: true,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 18,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 6
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_002&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The abstract activation selector has no supplied concrete encoding. Its Boolean placeholder preserves the CFG&#x27;s two supported activation choices without inventing a source-level test.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 16,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 14
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_007&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          1,
          2
        ],
        &quot;reason&quot;: &quot;The atomic call form exposes one normal response, not separately correlated exception and completion outputs. Source-backed placeholders retain this call&#x27;s exceptional value and Boolean control. Their availability remains restricted by the original CFG&#x27;s normal and exceptional continuations.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: true,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 16,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 15
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_010&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          0,
          1
        ],
        &quot;reason&quot;: &quot;Requests&#x27; internal status predicate and exception construction are absent. The local invocation effect and its outcome placeholders retain the status-check boundary; no response.json call occurs on the exceptional continuation.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 16,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 16
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_013&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          1,
          2
        ],
        &quot;reason&quot;: &quot;The normal decoded version and exceptional outcome belong to this same response.json invocation. The primitive vocabulary does not jointly bind those conditional outputs, so exception and completion placeholders retain their source occurrence and CFG-restricted availability.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 24,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 24
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_032&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          2,
          3
        ],
        &quot;reason&quot;: &quot;The conversion&#x27;s actual exception and normal-completion control require conditional outcome slots beyond the scalar compute result. Placeholders preserve those slots; neither successful integers nor request results supply the exception.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 19,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 15
          },
          {
            &quot;end_line&quot;: 28,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 27
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_039&quot;,
        &quot;locations&quot;: [
          &quot;api_key_environment&quot;
        ],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The Skill requires credential storage in a workspace .env file, but the implementation supplies no file loader or other file-to-process-environment handoff. This read therefore has process-environment provenance only; no file read, file ownership or storage execution is inferred.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 19,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 15
          },
          {
            &quot;end_line&quot;: 28,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 28
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_041&quot;,
        &quot;locations&quot;: [
          &quot;cse_id_environment&quot;
        ],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The documented .env entry and this environment lookup are not connected by an evidenced loader. The environment value remains distinct from any hypothetical stored-file version.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 28,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 26
          },
          {
            &quot;end_line&quot;: 35,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 23
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_045&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The example invokes skills/google-search/scripts/search.py, whereas the supplied implementation is skill/scripts/search.py. Their relationship is unestablished. If the command reaches this CLI, its query and credentials bind to the corresponding slots and its omitted count selects 5; execution of that handoff is not asserted.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 14,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 14
          },
          {
            &quot;end_line&quot;: 37,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 34
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_047&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          1,
          2
        ],
        &quot;reason&quot;: &quot;The normal HTTP response and actual raised exception are alternative outcomes of this CLI helper request. Outcome placeholders preserve this occurrence and the CFG-restricted availability, rather than treating an exception as successful API content.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: true,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 15,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 15
          },
          {
            &quot;end_line&quot;: 37,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 35
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_049&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          0,
          1
        ],
        &quot;reason&quot;: &quot;The supplied source does not expose Requests&#x27; internal status predicate or exception construction. The local effect and outcome placeholders preserve this helper invocation&#x27;s status check and its alternative continuation.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 16,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 16
          },
          {
            &quot;end_line&quot;: 37,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 35
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_051&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          1,
          2
        ],
        &quot;reason&quot;: &quot;Conditional exception and completion slots are retained with local placeholders for this decoding occurrence. They do not replace, alias or originate from its successful decoded content.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 37,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 35
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_053&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          2,
          3
        ],
        &quot;reason&quot;: &quot;Serialization&#x27;s conditional exception and completion slots are represented by source-backed placeholders. A serialization failure preserves the already received decoded results binding and supplies no successful formatted string.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 38,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 36
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_055&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          0,
          1
        ],
        &quot;reason&quot;: &quot;Print may raise after partial delivery. Outcome placeholders retain the actual print exception and normal-completion control; the supplied source establishes neither an exact delivered prefix nor rollback.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 28,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 21
          },
          {
            &quot;end_line&quot;: 39,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 6
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_057&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The Workflow is a placeholder. No per-element traversal, yield collection, save, later file read, retry, summarization or application-level shared-state update is supplied. No saved-result provenance or downstream model routing can be attached to this completion.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: true,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 39,
            &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
            &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
            &quot;start_line&quot;: 37
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_061&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;Error conversion and printing may themselves fail outside the protected try body. Their concrete exceptional payloads are not CFG outputs here; sys.exit(1) is reached only after those handler actions complete normally.&quot;,
        &quot;unmodeled&quot;: false,
        &quot;validation_errors&quot;: []
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_061&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;str_e&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_061/action_bindings&quot;
          },
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;error_sys_exit&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_061/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_053&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;json_dumps&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_053/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_051&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;cli.response_json&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_051/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_049&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;cli.raise_for_status&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_049/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_045&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;google_search_call&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_045/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_043&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;credential_sys_exit&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_043/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_032&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;int_count&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_032/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_028&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;usage_sys_exit&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_028/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_026&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;cli.argv_length&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_026/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_013&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;public.response_json&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_013/action_bindings&quot;
          }
        ]
      },
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [],
        &quot;instruction_id&quot;: &quot;ir_010&quot;,
        &quot;locations&quot;: [],
        &quot;origin&quot;: &quot;validation&quot;,
        &quot;outputs&quot;: [],
        &quot;reason&quot;: &quot;The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: [
          {
            &quot;code&quot;: &quot;source_action_role&quot;,
            &quot;message&quot;: &quot;Source action &#x27;public.raise_for_status&#x27; requires a real call at the instruction&#x27;s applicable control paths. A placeholder, output forwarding, or an operation in another alternative cannot establish this boundary. Use its actual declared location and interface inputs where required.&quot;,
            &quot;path&quot;: &quot;/ir_semantics/ir_010/action_bindings&quot;
          }
        ]
      }
    ],
    &quot;realizations&quot;: [
      {
        &quot;bindings&quot;: [],
        &quot;gaps&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 3,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 3
              },
              {
                &quot;end_line&quot;: 18,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 6
              }
            ],
            &quot;reason&quot;: &quot;The documented use condition has no receiving context slots or executable availability check. Neither the information need nor built-in web_search availability is established by the supplied activations.&quot;
          }
        ],
        &quot;requirement_id&quot;: &quot;R1&quot;,
        &quot;status&quot;: &quot;unmapped&quot;
      },
      {
        &quot;bindings&quot;: [],
        &quot;gaps&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 12,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 12
              },
              {
                &quot;end_line&quot;: 39,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 1
              }
            ],
            &quot;reason&quot;: &quot;Project creation and API enablement are documented setup obligations. No corresponding operation, resulting project or enabled-service state is supplied.&quot;
          }
        ],
        &quot;requirement_id&quot;: &quot;R2&quot;,
        &quot;status&quot;: &quot;unmapped&quot;
      },
      {
        &quot;bindings&quot;: [],
        &quot;gaps&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 13,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 13
              },
              {
                &quot;end_line&quot;: 27,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 27
              }
            ],
            &quot;reason&quot;: &quot;No key-generation operation or generated-key result is supplied. Reading a runtime credential does not establish its generation provenance.&quot;
          }
        ],
        &quot;requirement_id&quot;: &quot;R3&quot;,
        &quot;status&quot;: &quot;unmapped&quot;
      },
      {
        &quot;bindings&quot;: [],
        &quot;gaps&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 14
              },
              {
                &quot;end_line&quot;: 28,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 28
              }
            ],
            &quot;reason&quot;: &quot;No engine-creation operation or obtained CX result is supplied. The runtime identifier cannot establish that setup occurred or identify the engine that produced it.&quot;
          }
        ],
        &quot;requirement_id&quot;: &quot;R4&quot;,
        &quot;status&quot;: &quot;unmapped&quot;
      },
      {
        &quot;bindings&quot;: [],
        &quot;gaps&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 19,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 15
              },
              {
                &quot;end_line&quot;: 28,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 26
              },
              {
                &quot;end_line&quot;: 28,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 27
              }
            ],
            &quot;reason&quot;: &quot;No workspace .env write, saved credential payload or subsequent file read is supplied. The two process-environment reads have no evidenced handoff from the prescribed file; the example&#x27;s command-scoped variables do not establish that storage.&quot;
          }
        ],
        &quot;requirement_id&quot;: &quot;R5&quot;,
        &quot;status&quot;: &quot;unmapped&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;Receives this execution&#x27;s GOOGLE_API_KEY process-environment value.&quot;,
            &quot;target&quot;: {
              &quot;index&quot;: 0,
              &quot;instruction_id&quot;: &quot;ir_039&quot;,
              &quot;side&quot;: &quot;output&quot;
            }
          },
          {
            &quot;reason&quot;: &quot;Receives the separate GOOGLE_CSE_ID process-environment value.&quot;,
            &quot;target&quot;: {
              &quot;index&quot;: 0,
              &quot;instruction_id&quot;: &quot;ir_041&quot;,
              &quot;side&quot;: &quot;output&quot;
            }
          },
          {
            &quot;reason&quot;: &quot;Tests the actual received values for falsiness after both reads.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_042&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;The missing-credential branch delivers its error literal to stdout and invokes unsuccessful termination.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_043&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;Represents the branch&#x27;s exit with status 1.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_044&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R6&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;Receives the argv snapshot shared by the length test and query projection.&quot;,
            &quot;target&quot;: {
              &quot;index&quot;: 0,
              &quot;instruction_id&quot;: &quot;ir_024&quot;,
              &quot;side&quot;: &quot;output&quot;
            }
          },
          {
            &quot;reason&quot;: &quot;Produces the query from index 1 of that snapshot.&quot;,
            &quot;target&quot;: {
              &quot;index&quot;: 0,
              &quot;instruction_id&quot;: &quot;ir_030&quot;,
              &quot;side&quot;: &quot;output&quot;
            }
          },
          {
            &quot;reason&quot;: &quot;The insufficient-argument branch sends usage to stdout and invokes exit with status 1.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_028&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;constraints&quot;: [
          {
            &quot;condition&quot;: {
              &quot;instruction_id&quot;: &quot;ir_027&quot;,
              &quot;operation_path&quot;: [
                &quot;events&quot;,
                0,
                &quot;events&quot;,
                0,
                &quot;atomic_ops&quot;,
                0
              ],
              &quot;slot&quot;: {
                &quot;kind&quot;: &quot;self&quot;
              }
            },
            &quot;events&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_028&quot;,
                &quot;path&quot;: []
              }
            ],
            &quot;kind&quot;: &quot;only_if&quot;,
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            }
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R7&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;Projects argv index 2 and converts that argument with int when supplied.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_032&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;Provides the omission default 5.&quot;,
            &quot;target&quot;: {
              &quot;index&quot;: 0,
              &quot;instruction_id&quot;: &quot;ir_035&quot;,
              &quot;side&quot;: &quot;output&quot;
            }
          },
          {
            &quot;reason&quot;: &quot;Selects the parsed or default count from the actual predecessor. No additional range check is supplied; conversion failure propagates before credential reads and outside the later handler.&quot;,
            &quot;target&quot;: {
              &quot;index&quot;: 0,
              &quot;instruction_id&quot;: &quot;ir_037&quot;,
              &quot;side&quot;: &quot;output&quot;
            }
          }
        ],
        &quot;constraints&quot;: [
          {
            &quot;condition&quot;: {
              &quot;instruction_id&quot;: &quot;ir_031&quot;,
              &quot;operation_path&quot;: [
                &quot;events&quot;,
                0,
                &quot;events&quot;,
                0,
                &quot;atomic_ops&quot;,
                0
              ],
              &quot;slot&quot;: {
                &quot;kind&quot;: &quot;self&quot;
              }
            },
            &quot;events&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_032&quot;,
                &quot;path&quot;: []
              }
            ],
            &quot;kind&quot;: &quot;only_if&quot;,
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            }
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R8&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;Receives four separate bound public parameters, including the defaulted count when omitted.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_003&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;Constructs the public endpoint and parameter object with the four prescribed roles.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_005&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;Sends this public invocation&#x27;s URL and parameters to the remote search endpoint.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_007&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;Returns this public invocation&#x27;s decoded response to its caller without establishing further delivery or persistence.&quot;,
            &quot;target&quot;: {
              &quot;index&quot;: 0,
              &quot;instruction_id&quot;: &quot;ir_015&quot;,
              &quot;side&quot;: &quot;input&quot;
            }
          },
          {
            &quot;reason&quot;: &quot;Binds the CLI query, two runtime credentials and selected count to this helper invocation and constructs its request parameters.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_045&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;Performs the distinct CLI helper request using those parameters.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_047&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;The caller&#x27;s results binding receives this helper invocation&#x27;s decoded return, rather than its request parameters or HTTP response object.&quot;,
            &quot;target&quot;: {
              &quot;index&quot;: 0,
              &quot;instruction_id&quot;: &quot;ir_053&quot;,
              &quot;side&quot;: &quot;output&quot;
            }
          }
        ],
        &quot;gaps&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 27,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 27
              },
              {
                &quot;end_line&quot;: 35,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 23
              }
            ],
            &quot;reason&quot;: &quot;The documented example names a different script path. Its argument mapping is conditional on reaching this implementation; that handoff and an executed search are not established.&quot;
          }
        ],
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;status&quot;: &quot;partial&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;Receives the decoded helper return as results and serializes it into a separate JSON string.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_053&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;The actual presentation payload is the formatted JSON string delivered to process stdout. Its downstream audience and persistence are unspecified.&quot;,
            &quot;target&quot;: {
              &quot;index&quot;: 1,
              &quot;instruction_id&quot;: &quot;ir_055&quot;,
              &quot;side&quot;: &quot;input&quot;
            }
          }
        ],
        &quot;gaps&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 16,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 16
              },
              {
                &quot;end_line&quot;: 36,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 35
              }
            ],
            &quot;reason&quot;: &quot;The source serializes the complete decoded response but does not identify which response members constitute the required retrieved results. Necessity for every response field or the indentation choice cannot be inferred from that serialization.&quot;
          }
        ],
        &quot;requirement_id&quot;: &quot;R10&quot;,
        &quot;status&quot;: &quot;partial&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;Checks the public invocation&#x27;s actual response before decoding; a raised status error propagates to its caller.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_010&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;Checks the CLI helper response before decoding; failure enters the CLI exception dispatch.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_049&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;Selects the actual request, status, decoding, serialization or printing exception from its exceptional predecessor.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_058&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;For a matching Exception, binds that raised value, converts its message, prints the error to stdout and invokes exit with status 1 after successful handler actions.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_061&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;constraints&quot;: [
          {
            &quot;after&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_013&quot;,
                &quot;path&quot;: []
              }
            ],
            &quot;before&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_010&quot;,
                &quot;path&quot;: []
              }
            ],
            &quot;kind&quot;: &quot;requires_prior&quot;,
            &quot;matching&quot;: &quot;request&quot;,
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            }
          },
          {
            &quot;after&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_051&quot;,
                &quot;path&quot;: []
              }
            ],
            &quot;before&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_049&quot;,
                &quot;path&quot;: []
              }
            ],
            &quot;kind&quot;: &quot;requires_prior&quot;,
            &quot;matching&quot;: &quot;request&quot;,
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            }
          }
        ],
        &quot;gaps&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 39,
                &quot;file&quot;: &quot;skill/scripts/search.py&quot;,
                &quot;reason&quot;: &quot;Declaration citation; semantic support is not independently verified.&quot;,
                &quot;start_line&quot;: 37
              }
            ],
            &quot;reason&quot;: &quot;The normalized processing has no supported exception-class predicate connecting a particular raised value to handler membership. The source catches Exception; unmatched raised values propagate, and failures during handler conversion or printing do not reach its unsuccessful-exit action.&quot;
          }
        ],
        &quot;requirement_id&quot;: &quot;R11&quot;,
        &quot;status&quot;: &quot;partial&quot;
      }
    ],
    &quot;task_revision_id&quot;: &quot;646198c73dbfa4a8284caf63dc2131010757c342822dbc45b3ed40bf851c2b39&quot;
  }
}</pre>

</details>

