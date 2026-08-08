const fs = require('fs');
const path = require('path');
const Ajv = require('ajv');
const addFormats = require('ajv-formats');
const {
  buildTransferSecurityProfile,
  buildTransferSecurityProfileAsync
} = require('../security/transfer-analysis');

/**
 * JSON Schema for FCG output validation
 */
const fcgSchema = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["meta", "nodes", "edges", "source_sink", "paths", "statistics"],
  "properties": {
    "meta": {
      "type": "object",
      "required": ["skill_name", "analysis_timestamp"],
      "properties": {
        "skill_name": { "type": "string" },
        "skill_version": { "type": "string" },
        "analysis_timestamp": { "type": "string", "format": "date-time" },
        "analyzer_version": { "type": "string" },
        "input_source": { "type": "string" },
        "analysis_mode": { "type": "string", "enum": ["quick", "full", "deep"] }
      }
    },
    "nodes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "type"],
        "properties": {
          "id": { "type": "string" },
          "name": { "type": "string" },
          "type": { "type": "string", "enum": ["tool_call", "builtin_call", "custom_func"] },
          "category": { "type": "string", "enum": ["Source", "Sink", "Intermediate"] },
          "is_critical": { "type": "boolean" },
          "description": { "type": "string" },
          "location": {
            "type": "object",
            "properties": {
              "file": { "type": "string" },
              "line": { "type": "integer" },
              "section": { "type": "string" }
            }
          },
          "signature": {
            "type": "object",
            "properties": {
              "input": { "type": "object" },
              "output": { "type": "object" }
            }
          }
        }
      }
    },
    "edges": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "source", "target", "type"],
        "properties": {
          "id": { "type": "string" },
          "source": { "type": "string" },
          "target": { "type": "string" },
          "type": { "type": "string", "enum": ["data_dependency", "control_flow", "semantic", "doc_instruction"] },
          "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
          "validation_method": { "type": "string" },
          "is_feedback_edge": { "type": "boolean" },
          "feedback_removed_reason": { "type": "string" },
          "feedback_cycle_path": { "type": "array", "items": { "type": "string" } },
          "feedback_plausibility": { "type": "string", "enum": ["plausible", "implausible"] },
          "feedback_plausibility_source": { "type": "string", "enum": ["rule", "llm", "llm_fallback"] },
          "feedback_plausibility_reason": { "type": "string" },
          "data_flow": {
            "type": "object",
            "properties": {
              "from_param": { "type": "string" },
              "to_param": { "type": "string" },
              "data_type": { "type": "string" }
            }
          }
        }
      }
    },
    "source_sink": {
      "type": "object",
      "properties": {
        "sources": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "node_id": { "type": "string" },
              "reason": { "type": "string" },
              "data_type": { "type": "string" }
            }
          }
        },
        "sinks": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "node_id": { "type": "string" },
              "reason": { "type": "string" },
              "data_type": { "type": "string" },
              "is_critical": { "type": "boolean" }
            }
          }
        }
      }
    },
    "paths": {
      "type": "object",
      "properties": {
        "all_paths": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "path_id": { "type": "string" },
              "nodes": { "type": "array", "items": { "type": "string" } },
              "length": { "type": "integer" },
              "has_source": { "type": "boolean" },
              "has_sink": { "type": "boolean" },
              "is_complete": { "type": "boolean" },
              "source_node": { "type": "string" },
              "sink_node": { "type": "string" },
              "risk_level": { "type": "string", "enum": ["low", "medium", "high", "critical"] }
            }
          }
        },
        "source_to_sink_paths": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "path_id": { "type": "string" },
              "nodes": { "type": "array", "items": { "type": "string" } },
              "length": { "type": "integer" },
              "source_node": { "type": "string" },
              "sink_node": { "type": "string" },
              "risk_level": { "type": "string", "enum": ["low", "medium", "high", "critical"] }
            }
          }
        },
        "path_clusters": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "cluster_id": { "type": "string" },
              "semantic_template": { "type": "string" },
              "path_count": { "type": "integer" },
              "risk_distribution": {
                "type": "object",
                "properties": {
                  "critical": { "type": "integer" },
                  "high": { "type": "integer" },
                  "medium": { "type": "integer" },
                  "low": { "type": "integer" }
                }
              },
              "representative_path_id": { "type": "string" },
              "representative_path_nodes": { "type": "array", "items": { "type": "string" } },
              "representative_path_names": { "type": "array", "items": { "type": "string" } },
              "source_nodes": { "type": "array", "items": { "type": "string" } },
              "sink_nodes": { "type": "array", "items": { "type": "string" } },
              "source_names": { "type": "array", "items": { "type": "string" } },
              "sink_names": { "type": "array", "items": { "type": "string" } },
              "involved_modules": { "type": "array", "items": { "type": "string" } },
              "involved_triggers": { "type": "array", "items": { "type": "string" } },
              "involved_policies": { "type": "array", "items": { "type": "string" } },
              "involved_documents": { "type": "array", "items": { "type": "string" } },
              "path_ids": { "type": "array", "items": { "type": "string" } }
            }
          }
        },
        "source_to_sink_path_count_exact": { "type": "integer" },
        "path_compression": {
          "type": "object",
          "properties": {
            "exact_path_count": { "type": "integer" },
            "compression_nodes": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "id": { "type": "string" },
                  "original_node_id": { "type": "string" },
                  "original_name": { "type": "string" },
                  "member_node_ids": { "type": "array", "items": { "type": "string" } }
                }
              }
            },
            "compression_edges": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "id": { "type": "string" },
                  "source": { "type": "string" },
                  "target": { "type": "string" },
                  "source_compression_node": { "type": "string" },
                  "target_compression_node": { "type": "string" },
                  "member_node_ids": { "type": "array", "items": { "type": "string" } },
                  "middle_node_ids": { "type": "array", "items": { "type": "string" } },
                  "edge_count": { "type": "integer" }
                }
              }
            },
            "source_sink_pairs": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "source_node": { "type": "string" },
                  "sink_node": { "type": "string" },
                  "path_count": { "type": "integer" },
                  "representative_compression_edges": { "type": "array", "items": { "type": "string" } },
                  "representative_path_nodes": { "type": "array", "items": { "type": "string" } },
                  "representative_path_names": { "type": "array", "items": { "type": "string" } }
                }
              }
            }
          }
        }
      }
    },
    "statistics": {
      "type": "object",
      "properties": {
        "total_nodes": { "type": "integer" },
        "total_edges": { "type": "integer" },
        "source_count": { "type": "integer" },
        "sink_count": { "type": "integer" },
        "total_paths": { "type": "integer" },
        "source_to_sink_paths": { "type": "integer" },
        "high_risk_paths": { "type": "integer" },
        "feedback_edge_count": { "type": "integer" },
        "feedback_plausible_count": { "type": "integer" },
        "feedback_implausible_count": { "type": "integer" }
      }
    },
    "risks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "risk_id": { "type": "string" },
          "type": { "type": "string" },
          "path_id": { "type": "string" },
          "description": { "type": "string" },
          "severity": { "type": "string", "enum": ["low", "medium", "high", "critical"] }
        }
      }
    },
    "security_profile": {
      "type": "object",
      "properties": {
        "version": { "type": "string" },
        "node_profiles": { "type": "array" },
        "label_dictionary": { "type": "object" },
        "label_flows": { "type": "array" },
        "node_flow_sets": { "type": "array" },
        "provenance_graph": { "type": "object" },
        "observations": { "type": "array" },
        "statistics": { "type": "object" }
      }
    },
    "documentation_context": {
      "type": "object"
    }
  }
};

/**
 * Generate FCG JSON output from analysis results
 * @param {Object} analysisResult - Complete analysis result
 * @returns {Object} FCG JSON object
 */
function generateFCGJson(analysisResult, options = {}) {
  const fcgJson = buildBaseFCGJson(analysisResult);
  fcgJson.security_profile = buildTransferSecurityProfile({
    nodes: fcgJson.nodes,
    edges: fcgJson.edges,
    cycleExpand: Boolean(options.cycleExpand)
  });
  return fcgJson;
}

async function generateFCGJsonAsync(analysisResult, options = {}) {
  const fcgJson = buildBaseFCGJson(analysisResult);
  fcgJson.security_profile = await buildTransferSecurityProfileAsync({
    nodes: fcgJson.nodes,
    edges: fcgJson.edges,
    options
  });
  return fcgJson;
}

function buildBaseFCGJson(analysisResult) {
  const {
    skillData,
    graph,
    sourceSink = { sources: [], sinks: [] },
    paths = [],
    allPaths = [],
    pathCompression = { exact_path_count: 0, compression_nodes: [], compression_edges: [], source_sink_pairs: [] },
    pathClusters = [],
    documentationContext = {},
    dependencyStats = {},
    feedbackClassificationStats = null,
    semanticGateUsage = null,
    mode = 'full',
    inputSource = 'unknown'
  } = analysisResult;

  // Build nodes array
  const nodes = graph.getAllNodes().map(node => buildNodeJson(node));

  // Build edges array
  const edges = graph.getAllEdges().map((edge, index) => ({
    id: `edge_${String(index + 1).padStart(3, '0')}`,
    source: edge.source,
    target: edge.target,
    type: edge.type || 'data_dependency',
    confidence: edge.confidence || 0.5,
    validation_method: edge.validation_method || 'type_check',
    data_flow: edge.data_flow || {},
    semantic_reason: edge.semantic_reason || '',
    ...(edge.source_context !== undefined ? { source_context: edge.source_context } : {}),
    ...(edge.edge_evidence !== undefined ? { edge_evidence: edge.edge_evidence } : {}),
    ...(edge.is_feedback_edge ? {
      is_feedback_edge: true,
      feedback_removed_reason: edge.feedback_removed_reason || 'cycle_break',
      ...(Array.isArray(edge.feedback_cycle_path) ? { feedback_cycle_path: edge.feedback_cycle_path } : {}),
      ...(edge.feedback_plausibility ? {
        feedback_plausibility: edge.feedback_plausibility,
        feedback_plausibility_source: edge.feedback_plausibility_source || 'rule',
        ...(edge.feedback_plausibility_reason ? { feedback_plausibility_reason: edge.feedback_plausibility_reason } : {})
      } : {})
    } : {})
  }));

  // Calculate statistics
  const highRiskPaths = paths.filter(p => p.risk_level === 'high' || p.risk_level === 'critical').length;
  const exactSourceSinkCount = Number.isFinite(pathCompression?.exact_path_count)
    ? Number(pathCompression.exact_path_count)
    : paths.length;
  
  const statistics = {
    total_nodes: nodes.length,
    total_edges: edges.length,
    source_count: sourceSink.sources.length,
    sink_count: sourceSink.sinks.length,
    total_paths: allPaths.length,
    source_to_sink_paths: exactSourceSinkCount,
    high_risk_paths: highRiskPaths,
    feedback_edge_count: edges.filter(edge => edge.is_feedback_edge).length,
    feedback_plausible_count: edges.filter(edge => edge.feedback_plausibility === 'plausible').length,
    feedback_implausible_count: edges.filter(edge => edge.feedback_plausibility === 'implausible').length,
    ...(feedbackClassificationStats ? { feedback_classification: feedbackClassificationStats } : {}),
    ...dependencyStats,
    ...(semanticGateUsage ? { semantic_gate_llm_usage: semanticGateUsage } : {})
  };

  // Build risks array
  const risks = generateRisks(paths, nodes, edges);

  // Build final JSON
  const fcgJson = {
    meta: {
      skill_name: skillData.name,
      skill_version: skillData.version || '1.0.0',
      analysis_timestamp: new Date().toISOString(),
      analyzer_version: '1.0.0',
      input_source: inputSource,
      analysis_mode: mode
    },
    nodes,
    edges,
    source_sink: sourceSink,
    paths: {
      all_paths: allPaths,
      source_to_sink_paths: paths,
      path_clusters: pathClusters,
      source_to_sink_path_count_exact: exactSourceSinkCount,
      path_compression: pathCompression
    },
    statistics,
    risks,
    documentation_context: documentationContext || {}
  };

  return fcgJson;
}

function classifySinkCategory(dataType, node = {}, reason = '') {
  const text = combinedSecurityText(dataType, node, reason);
  if (/(llm|model|chat|completion|openai|anthropic|dashscope|qwen|gpt|claude|gemini)/i.test(text)) return 'model_inference';
  if (/(webhook|api|http|https|url|external|post|send|publish|share|upload)/i.test(text)) return 'external_network';
  if (/(exec|run|execute|shell|command|process|spawn)/i.test(text)) return 'command_execution';
  if (/(file|write|save|persist|append|markdown|document|artifact)/i.test(text)) return 'local_file_write';
  if (/(database|db|sql|insert|update|record|table|collection)/i.test(text)) return 'database_write';
  if (/(delete|remove|destroy)/i.test(text)) return 'destructive_operation';
  return 'generic_sink';
}

function classifyEgressType(dataType, node = {}, reason = '') {
  const category = classifySinkCategory(dataType, node, reason);
  if (category === 'model_inference') return 'model';
  if (category === 'external_network') return 'external_network';
  if (category === 'command_execution') return 'execution';
  if (category === 'local_file_write') return 'local_persistence';
  if (category === 'database_write') return 'database';
  if (category === 'destructive_operation') return 'destructive';
  return 'internal';
}

function combinedSecurityText(dataType, node = {}, reason = '') {
  const semantics = node.formal_semantics || {};
  const targets = Array.isArray(semantics.targets)
    ? semantics.targets.map(target => `${target.type || ''}:${target.value || ''}:${target.raw || ''}`).join(' ')
    : '';
  const effects = Array.isArray(semantics.effects) ? semantics.effects.join(' ') : '';
  return [
    dataType,
    reason,
    node.name,
    node.description,
    node.location?.file,
    targets,
    effects,
    JSON.stringify(node.signature || {})
  ].filter(Boolean).join(' ');
}

/**
 * Generate risks from paths
 * @param {Array} paths - Array of paths
 * @param {Array} nodes - Array of nodes
 * @param {Array} edges - Array of edges
 * @returns {Array} Array of risks
 */
function generateRisks(paths, nodes, edges) {
  const risks = [];
  
  for (const path of paths) {
    if (path.risk_level === 'high' || path.risk_level === 'critical') {
      // Check if path contains critical sink (data leakage)
      const hasCriticalSink = path.nodes.some(nodeId => {
        const node = nodes.find(n => n.id === nodeId);
        return node && node.is_critical;
      });
      
      risks.push({
        risk_id: `risk_${String(risks.length + 1).padStart(3, '0')}`,
        type: hasCriticalSink ? 'critical_data_leakage' : 'potential_data_over_exposure',
        path_id: path.path_id,
        description: hasCriticalSink 
          ? `Data flow path ${path.path_id} contains CRITICAL data leakage to external platform`
          : `Data flow path ${path.path_id} has ${path.risk_level} risk level`,
        severity: path.risk_level,
        evidence: {
          source_data: extractSourceData(path.data_transferred),
          sink_data: extractSinkData(path.data_transferred),
          data_minimization_violated: path.length > 3,
          has_critical_sink: hasCriticalSink
        },
        suggestion: hasCriticalSink 
          ? 'CRITICAL: Review data flow to external platform. Ensure no sensitive data is leaked.'
          : 'Review data flow and ensure minimal data transfer'
      });
    }
  }
  
  return risks;
}

function extractSourceData(transferText) {
  const text = String(transferText || '');
  if (text.includes(' -> ')) return text.split(' -> ')[0] || 'unknown';
  return 'unknown';
}

function extractSinkData(transferText) {
  const text = String(transferText || '');
  if (text.includes(' -> ')) return text.split(' -> ')[1] || 'unknown';
  return 'unknown';
}

/**
 * Validate FCG JSON against schema
 * @param {Object} fcgJson - FCG JSON object
 * @returns {Object} Validation result
 */
function validateFCGJson(fcgJson) {
  const ajv = new Ajv();
  addFormats(ajv);
  const validate = ajv.compile(fcgSchema);
  const valid = validate(fcgJson);
  
  return {
    valid,
    errors: validate.errors || []
  };
}

/**
 * Save FCG JSON to file
 * @param {Object} fcgJson - FCG JSON object
 * @param {string} outputPath - Output file path
 */
function saveToJson(fcgJson, outputPath) {
  const resolvedPath = path.resolve(outputPath);
  const outputDir = path.dirname(resolvedPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const _tSer = Date.now();
  const json = `${JSON.stringify(fcgJson)}\n`;
  if (process.env.FCG_PHASE_TIMING === '1') {
    process.stderr.write(`[phase] 6_json_stringify: ${((Date.now() - _tSer) / 1000).toFixed(2)}s bytes=${json.length}\n`);
  }
  const _tWrite = Date.now();
  fs.writeFileSync(resolvedPath, json, 'utf-8');
  if (process.env.FCG_PHASE_TIMING === '1') {
    process.stderr.write(`[phase] 7_fs_write: ${((Date.now() - _tWrite) / 1000).toFixed(2)}s\n`);
  }
  console.log(`FCG JSON saved to: ${resolvedPath}`);
}

function normalizeLocation(location = {}) {
  return {
    file: typeof location.file === 'string' ? location.file : '',
    line: Number.isInteger(location.line) ? location.line : Number(location.line) || 0,
    section: typeof location.section === 'string' ? location.section : ''
  };
}

function buildNodeJson(node) {
  const output = {
    id: node.id,
    name: node.name,
    type: node.type || 'tool_call',
    category: node.category || 'Intermediate',
    is_critical: Boolean(node.isCritical),
    description: node.description || '',
    location: normalizeLocation(node.location),
    signature: {
      input: node.input || {},
      output: node.output || {}
    }
  };

  const optionalFields = [
    'semanticKind',
    'action',
    'operationType',
    'extraction_method',
    'ownerDoc',
    'docRef',
    'docAction',
    'docActions',
    'stepIndex',
    'stepRange',
    'stepRefs',
    'instructionText',
    'member_step_count',
    'member_steps',
    'formal_semantics',
    'source_context',
    'semantic_gate',
    'ownerScript',
    'functionName',
    'callee',
    'excludeFromFlow',
    'excludeFromTypeAnalysis',
    'canonical_name',
    'callsite_id',
    'callsite_order',
    'callsite_role'
  ];

  for (const field of optionalFields) {
    if (node[field] !== undefined) {
      output[field] = node[field];
    }
  }

  return output;
}

module.exports = {
  generateFCGJson,
  generateFCGJsonAsync,
  validateFCGJson,
  saveToJson,
  fcgSchema
};

