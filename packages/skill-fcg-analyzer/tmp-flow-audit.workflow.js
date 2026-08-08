export const meta = {
  name: 'fcg-flow-semantic-audit',
  description: 'Audit first-30-skill FCG flows: per-flow semantic precision + completeness (recall) critic against source docs',
  phases: [
    { title: 'Precision', detail: 'walk each label_flow, flag semantically wrong nodes/paths/labels' },
    { title: 'Recall', detail: 'completeness critic: source sensitive source->sink transfers missing from the flow set' },
    { title: 'Synthesize', detail: 'rank findings across all 30 skills' }
  ]
}

// args: array of { base, fcgPath, srcDir } for the 30 skills.
// Each skill runs precision + recall independently (pipeline fan-out).

const SKILLS = Array.isArray(args) ? args : []
log(`Auditing ${SKILLS.length} skills (precision + recall each)`)

const FINDING_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    skill: { type: 'string' },
    dimension: { type: 'string', enum: ['precision', 'recall'] },
    flows_reviewed: { type: 'integer' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          severity: { type: 'string', enum: ['high', 'medium', 'low'] },
          kind: { type: 'string' },              // e.g. wrong-node-role, wrong-label, spurious-path, missing-flow, missing-sink
          label_flow_id: { type: 'string' },     // precision: which flow; recall: "" (it's a gap)
          node_or_path: { type: 'string' },      // node name(s) / path fragment involved
          summary: { type: 'string' },           // one sentence: what's wrong / missing
          evidence: { type: 'string' }           // source-doc quote or FCG field that grounds it
        },
        required: ['severity', 'kind', 'summary']
      }
    },
    notes: { type: 'string' }
  },
  required: ['skill', 'dimension', 'findings']
}

const PRECISION_PROMPT = (s) => `You are auditing the SEMANTIC PRECISION of an information-flow graph (FCG) extracted from an AI-agent "skill".

Source docs directory: ${s.srcDir}  (read SKILL.md first; also README.md, references/*.md, scripts/*.sh if present)
FCG output JSON: ${s.fcgPath}

The FCG models how sensitive data flows from sources (user query, files, secrets, external responses) through the skill to sinks (network calls, file writes, shell exec, logs). Read both.

CRITICAL — how to read a flow:
- Flows live in security_profile.label_flows[]. Each has node_path[] (node ids) and node_names[] (parallel human names) = the ordered path, plus edge_path[].
- The flowing datum's semantic label is NOT inline. Each flow carries label_id (a string). Dereference it: security_profile.label_dictionary[label_id] gives the full label object (label, category, subtype, sensitivity, evidence_text, reason, mode, confidence). If you read f.label directly it will be empty — you MUST use label_dictionary[f.label_id].
- Sinks/observations are in security_profile.observations[] (each links back via label_flow_ids[]). Node roles/tags are in security_profile.node_profiles[] keyed by node_id.

Your job: walk the flows and judge whether the nodes, paths, and labels make SEMANTIC sense given the source docs. Flag ONLY genuine problems (this is precision = false positives):
- a node assigned a wrong role (e.g. a pure doc/description node treated as a shell-exec sink; a user step mislabeled as a source);
- a label whose category/sensitivity contradicts what the source text actually describes;
- a path/edge that connects two things the source never links (spurious data dependency);
- a flow that clearly cannot happen per the source semantics.
Do NOT invent problems. If the flow set looks faithful, return few or zero findings. Sample intelligently if there are many flows (dedupe by (node_path signature, label) — many flows are the same shape). Report flows_reviewed.

Return the structured object. dimension="precision". Ground every finding with an evidence quote from the source doc or the exact FCG field.`

const RECALL_PROMPT = (s) => `You are the COMPLETENESS CRITIC (recall auditor) for an information-flow graph (FCG) extracted from an AI-agent "skill".

Source docs directory: ${s.srcDir}  (read SKILL.md first; also README.md, references/*.md, scripts/*.sh if present)
FCG output JSON: ${s.fcgPath}

Precision auditing (is what's there correct?) cannot find OMISSIONS. Your job is the opposite: find sensitive data movements the source docs describe that are MISSING from the FCG flow set.

Method (work from the SOURCE, not from the FCG — that's the whole point):
1. From the source docs, independently enumerate: every sensitive DATA SOURCE (user input/query, files read, API keys/secrets/env, external API responses, clipboard, etc.) and every EXFILTRATION SINK (network request, file write, shell command, log/telemetry, third-party API).
2. For each plausible source->sink transfer the skill can perform, check whether the FCG has a corresponding flow. To read FCG flows: security_profile.label_flows[] with node_path[]/node_names[]; the datum label is label_dictionary[label_id] (NOT inline f.label). Sinks are in observations[]. Node roles in node_profiles[].
3. Report every source->sink transfer that the docs support but the FCG has NO flow/observation for. Also report sources or sinks entirely absent from the graph.

Flag ONLY omissions you can ground in a specific source-doc quote. severity=high if a real exfiltration path (secret/user-data -> network/shell) is missing entirely; medium if a sink or source is present but under-connected; low if minor.

Return the structured object. dimension="recall". label_flow_id="" for gaps. Ground every finding with a source-doc quote.`

const results = await pipeline(
  SKILLS,
  // stage 1: precision + recall in parallel for this skill
  (s) => parallel([
    () => agent(PRECISION_PROMPT(s), { label: `prec:${s.base}`, phase: 'Precision', schema: FINDING_SCHEMA, agentType: 'general-purpose' }),
    () => agent(RECALL_PROMPT(s), { label: `rec:${s.base}`, phase: 'Recall', schema: FINDING_SCHEMA, agentType: 'general-purpose' })
  ]).then(([prec, rec]) => ({ base: s.base, prec, rec }))
)

const clean = results.filter(Boolean)
const allFindings = []
for (const r of clean) {
  for (const dim of [r.prec, r.rec]) {
    if (dim && Array.isArray(dim.findings)) {
      for (const f of dim.findings) allFindings.push({ skill: r.base, dimension: dim.dimension, ...f })
    }
  }
}

log(`Collected ${allFindings.length} raw findings across ${clean.length} skills`)

// synthesize: rank + cluster
const SYNTH_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    systemic_precision_issues: { type: 'array', items: { type: 'string' } },  // patterns recurring across skills
    systemic_recall_issues: { type: 'array', items: { type: 'string' } },
    top_findings: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          rank: { type: 'integer' },
          skill: { type: 'string' },
          dimension: { type: 'string' },
          severity: { type: 'string' },
          kind: { type: 'string' },
          summary: { type: 'string' }
        },
        required: ['skill', 'dimension', 'severity', 'summary']
      }
    },
    recall_method_note: { type: 'string' }  // how well the completeness-critic approach worked, its blind spots
  },
  required: ['top_findings']
}

const synthesis = await agent(
  `You are synthesizing an FCG flow-audit across ${clean.length} skills. Here are all raw findings as JSON:\n\n${JSON.stringify(allFindings).slice(0, 60000)}\n\nProduce: (1) systemic precision issues = wrong-extraction patterns that recur across multiple skills (these matter most — they point to analyzer bugs, not one-off skill quirks); (2) systemic recall issues = kinds of flows the extractor systematically misses; (3) top_findings ranked most-severe-first (high severity + recurring first); (4) recall_method_note: an honest assessment of how well the "completeness critic reads source independently" method worked and what it still cannot catch. Be concrete.`,
  { label: 'synthesize', phase: 'Synthesize', schema: SYNTH_SCHEMA, agentType: 'general-purpose' }
)

return { skills_audited: clean.length, raw_finding_count: allFindings.length, synthesis, per_skill: clean.map(r => ({ base: r.base, precision_findings: r.prec?.findings?.length || 0, recall_findings: r.rec?.findings?.length || 0 })) }
