#!/usr/bin/env node

require('../../../shared/load-env.cjs').loadProjectEnv({ entryFile: __filename });

/**
 * Skill FCG Analyzer - Main Entry Point
 * Analyzes OpenClaw Skills and builds Function Call Graphs
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const AdmZip = require('adm-zip');

// Import modules
const { parseSkill, parseReadme, findExecutableFiles } = require('./parser/skill-parser');
const { extractToolCalls } = require('./parser/tool-extractor');
const {
  extractDocumentFlow,
  resolvePendingConstraints,
  newSemanticGateUsage,
  summarizeSemanticGateUsage
} = require('./parser/doc-flow-extractor');
const { extractScriptFlow } = require('./parser/script-flow-extractor');
const { buildDocumentationPlan } = require('./parser/document-context');
const { analyzeTypeCompatibility } = require('./parser/type-analyzer');
const { buildFCG, removeDuplicateEdges } = require('./analyzer/fcg-builder');
const { validatePairs } = require('./analyzer/llm-validator');
const { removeCycles, detectAndTagCycles, breakOnlyFake } = require('./analyzer/cycle-remover');
const { classifyFeedbackEdges, resolveFeedbackLlmReview } = require('./analyzer/feedback-edge-classifier');
const { splitGraphNodes } = require('./analyzer/node-splitter');
const { buildCallSiteMediation, buildEndpointMaps, expandAndMapEdges } = require('./analyzer/callsite-expander');
const {
  extractAllPaths
} = require('./analyzer/path-extractor');
const { generateFCGJson, generateFCGJsonAsync, validateFCGJson, saveToJson } = require('./output/json-generator');
const { saveFlowchartArtifacts, deriveFlowchartPaths } = require('./output/flowchart-generator');

/**
 * SkillFCGAnalyzer class
 */
class SkillFCGAnalyzer {
  /**
   * Create analyzer instance
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    this.llmProvider = options.llmProvider || process.env.LLM_PROVIDER || 'openai';
    this.llmModel = options.llmModel || process.env.LLM_MODEL || 'gpt-5.5';
    // Explicit option wins over the env var (so a caller can force LLM on/off
    // regardless of an ambient FCG_DISABLE_LLM=1); env var is the fallback.
    this.disableLlm = typeof options.disableLlm === 'boolean'
      ? options.disableLlm
      : isTruthyEnv(process.env.FCG_DISABLE_LLM);
    this.llmApiKey = Object.prototype.hasOwnProperty.call(options, 'llmApiKey')
      ? (this.disableLlm ? '' : options.llmApiKey)
      : (process.env.LLM_API_KEY || '');
    if (this.disableLlm) this.llmApiKey = '';
    // gpt-5.5 is a reasoning model: a single real semantic-gate / judge call runs
    // 50-100s (completion+reasoning time, not prompt size). The old 30s default was
    // BELOW real latency, so calls timed out and postJsonWithTimeout retried them as
    // transient — stalling whole batches with empty logs. 180s covers real latency
    // with headroom; a genuinely hung call still fails (3x180s worst case) but that
    // no longer masks normal completions. Aligns with the DOE judge default.
    this.llmTimeout = options.llmTimeout || 180000;
    this.llmEndpoint = options.llmEndpoint || '';
    // Feedback-edge plausibility LLM review: option overrides env (resolved by
    // resolveFeedbackLlmReview at call time, default ON). undefined = use env.
    this.feedbackLlmReview = options.feedbackLlmReview;
    // Cycle expansion: when on, real (plausible) cycles are NOT physically broken
    // — they survive into the transfer layer to expand one lap (periodic leaks /
    // collapse). Now DEFAULT ON: the transfer flood has no wall-clock/size caps by
    // default (see graph-transfer-analyzer DEFAULT_LIMITS) so the one-lap expansion
    // always runs to convergence, even on the largest skills. Set FCG_CYCLE_EXPAND=0
    // (or option cycleExpand:false) to fall back to build-time cycle breaking.
    // Option overrides env; env unset means on.
    this.cycleExpand = typeof options.cycleExpand === 'boolean'
      ? options.cycleExpand
      : !isFalsyEnv(process.env.FCG_CYCLE_EXPAND);
    this.mode = options.mode || 'full';
    this.semanticLlm = options.semanticLlm !== false && !this.disableLlm;
    this.labelLlmAssist = Boolean(options.labelLlmAssist);
    this.labelLlmConcurrency = Number(options.labelLlmConcurrency || 2);
    this.labelLlmCache = options.labelLlmCache || '';
    this.semanticRefiner = options.semanticRefiner;
    this.maxDependencyCandidates = normalizePositiveInteger(
      options.maxDependencyCandidates ?? process.env.FCG_DEPENDENCY_MAX_CANDIDATES,
      2000
    );
    this.dependencyLlmPolicy = normalizeDependencyLlmPolicy(
      options.dependencyLlmPolicy ?? process.env.FCG_DEPENDENCY_LLM_POLICY ?? 'high_value'
    );
    this.dependencyLlmMaxPairs = normalizePositiveInteger(
      options.dependencyLlmMaxPairs ?? process.env.FCG_DEPENDENCY_LLM_MAX_PAIRS,
      32
    );
    this.dependencyLlmBatchSize = normalizePositiveInteger(
      options.dependencyLlmBatchSize ?? process.env.FCG_DEPENDENCY_LLM_BATCH_SIZE,
      16
    );
    this.dependencyLlmCache = Object.prototype.hasOwnProperty.call(options, 'dependencyLlmCache')
      ? options.dependencyLlmCache
      : process.env.FCG_DEPENDENCY_LLM_CACHE;
    this.maxDocFlowNodes = normalizeNonNegativeInteger(
      options.maxDocFlowNodes ?? process.env.FCG_MAX_DOC_FLOW_NODES,
      0
    );
    this.semanticGateBatchSize = normalizePositiveInteger(
      options.semanticGateBatchSize ?? process.env.FCG_SEMANTIC_GATE_BATCH_SIZE,
      10
    );
    this.semanticGateConcurrency = normalizePositiveInteger(
      options.semanticGateConcurrency ?? process.env.FCG_SEMANTIC_GATE_CONCURRENCY,
      4
    );
    this.semanticGateMaxBatchChars = normalizePositiveInteger(
      options.semanticGateMaxBatchChars ?? process.env.FCG_SEMANTIC_GATE_MAX_BATCH_CHARS,
      60000
    );
    this.semanticGateCache = Object.prototype.hasOwnProperty.call(options, 'semanticGateCache')
      ? options.semanticGateCache
      : process.env.FCG_SEMANTIC_GATE_CACHE;
    this.scriptSemanticRefiner = options.scriptSemanticRefiner;
    this.scriptSemanticBatchRefiner = options.scriptSemanticBatchRefiner;
    this.constraintEndpointResolver = options.constraintEndpointResolver;
    this.maxCallsiteMediationNodes = normalizeNonNegativeInteger(
      options.maxCallsiteMediationNodes ?? process.env.FCG_MAX_CALLSITE_MEDIATION_NODES,
      0
    );
    this.labelAssistant = options.labelAssistant;
    this.tempDir = null;
    this.tempZipPath = null;
  }

  /**
   * Analyze a skill from local zip file or directory
   * @param {string} inputPath - Path to zip file or skill directory
   * @returns {Promise<Object>} Analysis result
   */
  async analyze(inputPath) {
    console.log(`Starting analysis: ${inputPath}`);
    const startTime = Date.now();

    try {
      if (isHttpUrl(inputPath)) {
        return this.analyzeFromUrl(inputPath);
      }
      if (this.labelLlmAssist && !String(this.llmApiKey || '').trim()) {
        throw new Error('LLM_API_KEY is required when --label-llm-assist is enabled');
      }
      if (this.semanticLlm && !String(this.llmApiKey || '').trim()) {
        throw new Error('LLM_API_KEY is required for FCG Markdown semantic gate');
      }

      // Phase 1: Parse input
      const skillRootDir = await this.prepareInput(inputPath);
      console.log(`[ok] Input prepared: ${skillRootDir}`);

      // Phase 2: Parse skill files
      const skillData = parseSkill(skillRootDir);
      const readmeData = parseReadme(skillRootDir);
      const executableFiles = findExecutableFiles(skillRootDir);
      const documentationPlan = buildDocumentationPlan(skillData, readmeData, executableFiles);
      console.log(`[ok] Skill parsed: ${skillData.name}`);

      // Phase 3: Extract tool calls
      const tools = extractToolCalls(skillData, readmeData, executableFiles, {
        markdownDocs: documentationPlan.extractionDocs,
        rootDir: skillRootDir
      });
      console.log(`[ok] Tools extracted: ${tools.length}`);

      const scriptFlow = await extractScriptFlow(executableFiles, {
        rootDir: skillRootDir,
        semanticLlm: this.semanticLlm,
        disableLlm: this.disableLlm,
        llmProvider: this.llmProvider,
        llmModel: this.llmModel,
        llmApiKey: this.llmApiKey,
        llmEndpoint: this.llmEndpoint,
        llmTimeout: this.llmTimeout,
        scriptSemanticRefiner: this.scriptSemanticRefiner,
        scriptSemanticBatchRefiner: this.scriptSemanticBatchRefiner
      });
      if (scriptFlow.nodes.length > 0) {
        tools.push(...scriptFlow.nodes);
        console.log(`[ok] Script flow extracted: ${scriptFlow.nodes.length} nodes, ${scriptFlow.edges.length} edges`);
      }

      let documentFlowEdges = [...scriptFlow.edges];
      let semanticGateUsage = null;
      {
        const documentFlow = await extractDocumentFlow(skillData, readmeData, {
          extractionDocs: documentationPlan.extractionDocs,
          reviewDocs: documentationPlan.reviewDocs,
          documentationContext: documentationPlan.documentationContext,
          semanticLlm: this.semanticLlm,
          llmProvider: this.llmProvider,
          llmModel: this.llmModel,
          llmApiKey: this.llmApiKey,
          llmEndpoint: this.llmEndpoint,
          llmTimeout: this.llmTimeout,
          disableLlm: this.disableLlm,
          semanticRefiner: this.semanticRefiner,
          maxDocFlowNodes: this.maxDocFlowNodes,
          semanticGateBatchSize: this.semanticGateBatchSize,
          semanticGateConcurrency: this.semanticGateConcurrency,
          semanticGateMaxBatchChars: this.semanticGateMaxBatchChars,
          semanticGateCache: this.semanticGateCache
        });
        const limitedDocumentFlow = limitDocumentFlow(documentFlow, this.maxDocFlowNodes);
        if (limitedDocumentFlow.truncated) {
          console.warn(
            `Warning: doc-flow nodes capped at ${limitedDocumentFlow.nodes.length}/${documentFlow.nodes.length}; ` +
            `set FCG_MAX_DOC_FLOW_NODES to adjust batch breadth.`
          );
        }
        if (limitedDocumentFlow.nodes.length > 0) {
          tools.push(...limitedDocumentFlow.nodes);
        }
        documentFlowEdges.push(...limitedDocumentFlow.edges);
        semanticGateUsage = documentFlow.semantic_gate_usage || null;
        console.log(`[ok] Doc flow extracted: ${limitedDocumentFlow.nodes.length} nodes, ${limitedDocumentFlow.edges.length} edges`);
        if (semanticGateUsage) {
          console.log(`[ok] Semantic gate LLM usage: ${semanticGateUsage.calls} calls, ${semanticGateUsage.prompt_tokens} prompt tok, cache hit ${(semanticGateUsage.prompt_cache_hit_ratio * 100).toFixed(1)}%`);
        }
      }

      // Add implicit user query source (OpenClaw activation flow)
      const { createUserQuerySource } = require('./classifier/source-sink');
      const userQueryNode = createUserQuerySource();
      tools.unshift(userQueryNode); // Add as first node
      console.log(`[ok] Added implicit user query source`);

      const mediation = buildCallSiteMediation(tools);
      const limitedMediation = limitMediation(mediation, tools, this.maxCallsiteMediationNodes);
      if (limitedMediation.truncated) {
        console.warn(
          `Warning: call-site mediation nodes capped at ${limitedMediation.nodes.length}/${mediation.nodes.length}; ` +
          `set FCG_MAX_CALLSITE_MEDIATION_NODES to adjust batch breadth.`
        );
      }
      if (limitedMediation.nodes.length > 0) {
        tools.push(...limitedMediation.nodes);
        documentFlowEdges.push(...limitedMediation.edges);
        console.log(`[ok] Added call-site LLM mediation: ${limitedMediation.nodes.length} nodes, ${limitedMediation.edges.length} edges`);
      }

      // Global two-phase constraint resolution. Every node source is now merged
      // into `tools`, so ordering-kind prohibitive constraints (e.g. "vet must
      // precede install", stashed as node.pending_constraint during the doc
      // semantic gate) can match their endpoints against the FULL node set
      // (tool-call / script / doc / mediation) before falling back to synthesis.
      // This is why resolution runs here and not inside extractDocumentFlow:
      // an endpoint like "install" may be a tool or script node, not a doc node.
      {
        const constraintGateUsage = newSemanticGateUsage();
        const resolved = await resolvePendingConstraints(tools, {
          llmProvider: this.llmProvider,
          llmModel: this.llmModel,
          llmApiKey: this.llmApiKey,
          llmEndpoint: this.llmEndpoint,
          llmTimeout: this.llmTimeout,
          disableLlm: this.disableLlm,
          semanticGateUsage: constraintGateUsage,
          constraintEndpointResolver: this.constraintEndpointResolver
        });
        // Fold constraint-endpoint LLM usage into the doc-flow gate total so the
        // statistics reflect every gate-family LLM call this run made.
        const constraintUsageSummary = summarizeSemanticGateUsage(constraintGateUsage);
        if (constraintUsageSummary) {
          semanticGateUsage = mergeSemanticGateUsage(semanticGateUsage, constraintUsageSummary);
        }
        if (resolved.addedNodes.length > 0) {
          tools.push(...resolved.addedNodes);
        }
        if (resolved.edges.length > 0) {
          documentFlowEdges.push(...resolved.edges);
          console.log(`[ok] Resolved prohibitive-ordering constraints: ${resolved.edges.length} edges, ${resolved.addedNodes.length} synthesized endpoint(s)`);
        }
      }

      // Phase 4: Sparse dependency candidate analysis
      const dependencyCandidates = analyzeTypeCompatibility(tools, {
        maxCandidates: this.maxDependencyCandidates
      });
      const dependencyCandidateStats = dependencyCandidates.statistics || {};
      console.log(`[ok] Dependency candidates: ${dependencyCandidates.length}`);

      // Add edges from user query to LLM inference (implicit data flow)
      const structuralDependencyEdges = [];
      const llmNodeIndex = tools.findIndex(t => t.name === 'llm.inference');
      if (llmNodeIndex !== -1) {
        structuralDependencyEdges.push({
          source: userQueryNode.name,
          target: tools[llmNodeIndex].name,
          type: 'data_dependency',
          confidence: 1.0,
          validation_method: 'dependency_structural',
          data_flow: {
            from_param: 'query_text',
            to_param: 'user_query',
            data_type: 'string'
          },
          semantic_reason: 'Implicit OpenClaw activation query flows to LLM inference'
        });
        console.log(`[ok] Added user query -> LLM inference edge`);
      }

      // Add edges from non-callsite nodes to global LLM inference (Skill content flows to LLM).
      // Runtime tool call-sites use per-call mediation nodes instead to avoid global LLM cycles.
      if (llmNodeIndex !== -1) {
        const llmNode = tools[llmNodeIndex];
        for (let i = 1; i < tools.length; i++) { // Skip user query (index 0)
          if (i === llmNodeIndex) continue;
          const tool = tools[i];
          if (tool.name === 'llm.inference') continue;
          if (!shouldAddImplicitToolToLlmEdge(tool)) continue;
          
          const exists = structuralDependencyEdges.some(edge =>
            edge.source === tool.name && edge.target === llmNode.name
          );
          
          if (!exists) {
            structuralDependencyEdges.push({
              source: tool.name,
              target: llmNode.name,
              type: 'data_dependency',
              confidence: 0.9,
              validation_method: 'dependency_structural',
              data_flow: {
                from_param: 'skill_content',
                to_param: 'skill_content',
                data_type: 'string'
              },
              semantic_reason: 'Skill content is available to the global LLM context'
            });
          }
        }
        console.log(`[ok] Added tool -> LLM inference edges`);
      }

      // Phase 5: High-value dependency LLM validation (skip in quick mode)
      let validatedEdges = [];
      let dependencyValidationStats = {};
      if (this.mode !== 'quick') {
        validatedEdges = await validatePairs(dependencyCandidates, {
          provider: this.llmProvider,
          model: this.llmModel,
          apiKey: this.llmApiKey,
          timeout: this.llmTimeout,
          endpoint: this.llmEndpoint,
          disableLlm: this.disableLlm,
          dependencyLlmPolicy: this.dependencyLlmPolicy,
          dependencyLlmMaxPairs: this.dependencyLlmMaxPairs,
          dependencyLlmBatchSize: this.dependencyLlmBatchSize,
          dependencyLlmCache: this.dependencyLlmCache
        });
        dependencyValidationStats = validatedEdges.statistics || {};
        console.log(`[ok] Validated dependency edges: ${validatedEdges.length}`);
      } else {
        validatedEdges = dependencyCandidates.map((pair, index) => ({
          id: `edge_${String(index + 1).padStart(3, '0')}`,
          source: pair.source.name,
          target: pair.target.name,
          type: 'data_dependency',
          confidence: pair.confidence,
          validation_method: 'dependency_rule',
          data_flow: {
            from_param: pair.compatibleParams[0]?.fromParam || 'unknown',
            to_param: pair.compatibleParams[0]?.toParam || 'unknown',
            data_type: pair.compatibleParams[0]?.fromType || 'string'
          },
          semantic_reason: pair.candidate_reason || 'Sparse dependency rule'
        }));
        dependencyValidationStats = {
          dependency_llm_policy: 'quick_mode',
          dependency_llm_candidate_count: 0,
          dependency_llm_validated_count: 0,
          dependency_llm_cache_hit_count: 0,
          dependency_llm_request_count: 0,
          dependency_llm_error_count: 0
        };
        console.log(`[ok] Quick dependency edges: ${validatedEdges.length}`);
      }
      validatedEdges.push(...structuralDependencyEdges);

      // Deep mode: include additional structural control-flow edges.
      let deepModeEdges = [];
      if (this.mode === 'deep') {
        deepModeEdges = buildDeepModeEdges(tools);
        console.log(`[ok] Deep mode structural edges: ${deepModeEdges.length}`);
      }

      // Map edge source/target from unique node names or canonical tool names to node IDs.
      const endpointMaps = buildEndpointMaps(tools);
      validatedEdges = expandAndMapEdges(validatedEdges, endpointMaps);
      deepModeEdges = expandAndMapEdges(deepModeEdges, endpointMaps);
      documentFlowEdges = expandAndMapEdges(documentFlowEdges, endpointMaps);

      // Phase 6: Build FCG
      let graph = buildFCG(tools, [...validatedEdges, ...deepModeEdges, ...documentFlowEdges]);
      graph = removeDuplicateEdges(graph);
      // Cycle handling is decision-first when cycleExpand is on: tag cycles, then
      // let the plausibility classifier below decide which physically break.
      // - cycleExpand OFF (default): removeCycles breaks ALL cycles now; the
      //   classifier that follows is advisory-only (byte-identical to pre-feature
      //   behavior).
      // - cycleExpand ON: detectAndTagCycles only tags (adjacency untouched);
      //   breakOnlyFake (after classification) removes just the implausible/fake
      //   cycles, leaving real cycles in adjacency for the transfer layer to
      //   expand one lap.
      if (this.cycleExpand) {
        graph = detectAndTagCycles(graph);
      } else {
        graph = removeCycles(graph);
      }
      console.log(`[ok] FCG built: ${graph.nodes.size} nodes, ${graph.edges.length} edges`);

      // Classify each cycle-broken feedback edge by plausibility (is this back-edge
      // a genuine self-optimizing loop, or a dedup/structural artifact?). Coarse
      // rule pass biased for recall (wide net), then an optional LLM review that
      // only rescues rule-implausible edges. When cycleExpand is off this is
      // advisory metadata only; when on it also drives breakOnlyFake below.
      const feedbackClassificationStats = await classifyFeedbackEdges(graph, {
        provider: this.llmProvider,
        model: this.llmModel,
        apiKey: this.llmApiKey,
        timeout: this.llmTimeout,
        endpoint: this.llmEndpoint,
        disableLlm: this.disableLlm,
        feedbackLlmReview: resolveFeedbackLlmReview(this.feedbackLlmReview)
      });
      if (feedbackClassificationStats.feedback_edge_count > 0) {
        console.log(`[ok] Feedback edges classified: ${feedbackClassificationStats.rule_plausible_count} plausible, ${feedbackClassificationStats.rule_implausible_count} implausible (llm rescued ${feedbackClassificationStats.llm_rescued_count})`);
      }

      // With cycleExpand on, physically break ONLY fake cycles now that
      // plausibility is known; real cycles remain traversable in adjacencyList.
      if (this.cycleExpand) {
        graph = breakOnlyFake(graph);
      }

      // Enforce the single-crossing invariant deterministically, AFTER edges are
      // resolved to node ids. Split children inherit the parent's edges (no
      // re-pairing). Each resulting node crosses at most one data boundary, so
      // observation<->sink-node is 1:1 downstream.
      const preSplitNodeCount = graph.nodes.size;
      graph = splitGraphNodes(graph);
      if (graph.nodes.size !== preSplitNodeCount) {
        console.log(`[ok] Node split (single-crossing invariant): ${preSplitNodeCount} -> ${graph.nodes.size} nodes, ${graph.edges.length} edges`);
      }

      // Phase 7: Extract debug paths only. Security analysis is graph-wide in security_profile 2.0.
      // NOTE these caps are intentionally NOT lifted to no-limit like the transfer
      // flood's are. The flood (graph-transfer-analyzer) is a linear-convergent
      // computation whose size gates were pure result-size ceilings, so removing
      // them just lets correct analysis finish. This all-simple-path enumeration is
      // different: it is O(V!) in the worst case (bounded only by !path.includes),
      // so "guaranteed to terminate" here can mean days on a dense graph. And it
      // feeds ONLY debug output — no security verdict depends on it. So these
      // remain bounded on purpose; they gate a convenience listing, not a result.
      const { sourceSink, pathCompression, paths } = buildLegacyDebugOutputs();
      const allPaths = extractAllPaths(graph, {
        maxAllPathsTotal: 1500,
        maxNeighborPaths: 1,
        maxPathLength: 12,
        maxStateExpansionsPerSearch: 1500
      });
      const pathClusters = [];
      console.log(`[ok] Debug paths extracted: ${allPaths.length} total`);
      if (process.env.FCG_PHASE_TIMING === '1') {
        process.stderr.write(`[phase] 0_pre_transfer(parse+gate+build+split+debugpaths): ${((Date.now() - startTime) / 1000).toFixed(2)}s\n`);
      }

      // Phase 9: Generate output
      const analysisResult = {
        skillData,
        tools,
        graph,
        sourceSink,
        paths,
        allPaths,
        pathCompression,
        pathClusters,
        documentationContext: documentationPlan.documentationContext,
        dependencyStats: {
          ...dependencyCandidateStats,
          ...dependencyValidationStats
        },
        feedbackClassificationStats,
        semanticGateUsage,
        mode: this.mode,
        inputSource: inputPath
      };

      const fcgJson = this.labelLlmAssist
        ? await generateFCGJsonAsync(analysisResult, {
            labelLlmAssist: this.labelLlmAssist,
            labelLlmConcurrency: this.labelLlmConcurrency,
            labelLlmCache: this.labelLlmCache || defaultLabelLlmCachePath(inputPath),
            llmProvider: this.llmProvider,
            llmModel: this.llmModel,
            llmApiKey: this.llmApiKey,
            llmEndpoint: this.llmEndpoint,
            llmTimeout: this.llmTimeout,
            labelAssistant: this.labelAssistant,
            cycleExpand: this.cycleExpand
          })
        : generateFCGJson(analysisResult, { cycleExpand: this.cycleExpand });

      // Validate output
      const validation = validateFCGJson(fcgJson);
      if (!validation.valid) {
        console.warn('Warning: Output validation failed:', validation.errors);
      }

      const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
      console.log(`\n[ok] Analysis completed in ${elapsed}s`);
      console.log(`  Nodes: ${fcgJson.statistics.total_nodes}`);
      console.log(`  Edges: ${fcgJson.statistics.total_edges}`);
      console.log(`  Transfer observations: ${fcgJson.security_profile.statistics.observation_count}`);
      console.log(`  Label flows: ${fcgJson.security_profile.statistics.label_flow_count}`);

      return fcgJson;

    } catch (error) {
      console.error(`Analysis failed: ${error.message}`);
      throw error;
    } finally {
      // Cleanup temp directory
      this.cleanup();
    }
  }

  /**
   * Analyze a skill from Clawhub URL
   * @param {string} url - Clawhub URL
   * @returns {Promise<Object>} Analysis result
   */
  async analyzeFromUrl(url) {
    console.log(`Downloading from URL: ${url}`);
    
    // Extract skill name from URL
    const urlParts = url.split('/');
    const skillName = urlParts[urlParts.length - 1] || 'unknown-skill';
    
    // Download zip file
    const zipPath = await this.downloadZip(url, skillName);
    
    // Analyze the downloaded zip
    return this.analyze(zipPath);
  }

  /**
   * Prepare input (extract zip or validate directory)
   * @param {string} inputPath - Input path
   * @returns {Promise<string>} Skill root directory
   */
  async prepareInput(inputPath) {
    if (inputPath.endsWith('.zip')) {
      return this.extractZip(inputPath);
    } else if (fs.existsSync(inputPath) && fs.statSync(inputPath).isDirectory()) {
      return inputPath;
    } else {
      throw new Error(`Invalid input path: ${inputPath}`);
    }
  }

  /**
   * Extract zip file to temp directory
   * @param {string} zipPath - Path to zip file
   * @returns {string} Extracted directory path
   */
  extractZip(zipPath) {
    const zip = new AdmZip(zipPath);
    this.tempDir = path.join(os.tmpdir(), `skill-fcg-${Date.now()}`);
    
    zip.extractAllTo(this.tempDir, true);
    
    // Find the skill root (might be nested)
    const entries = fs.readdirSync(this.tempDir);
    if (entries.length === 1 && fs.statSync(path.join(this.tempDir, entries[0])).isDirectory()) {
      return path.join(this.tempDir, entries[0]);
    }
    
    return this.tempDir;
  }

  /**
   * Download zip file from URL
   * @param {string} url - URL to download
   * @param {string} skillName - Skill name for filename
   * @returns {Promise<string>} Path to downloaded zip
   */
  async downloadZip(url, skillName) {
    const fetch = (await import('node-fetch')).default;
    const zipPath = path.join(os.tmpdir(), `${sanitizeFileName(skillName)}-${Date.now()}.zip`);

    console.log(`Downloading: ${url}`);
    const response = await fetchWithTimeout(fetch, url, this.llmTimeout);

    if (!response.ok) {
      throw new Error(`Download failed: ${response.status} ${response.statusText}`);
    }

    let downloadResponse = response;
    const contentType = (response.headers.get('content-type') || '').toLowerCase();

    if (!isZipPayload(url, contentType)) {
      const html = await response.text();
      const resolvedUrl = resolveZipUrl(url, html);
      if (!resolvedUrl) {
        throw new Error('Could not find downloadable zip link from the provided URL');
      }

      console.log(`Resolved zip download URL: ${resolvedUrl}`);
      downloadResponse = await fetchWithTimeout(fetch, resolvedUrl, this.llmTimeout);
      if (!downloadResponse.ok) {
        throw new Error(`Download failed: ${downloadResponse.status} ${downloadResponse.statusText}`);
      }
    }

    const buffer = await downloadResponse.buffer();
    fs.writeFileSync(zipPath, buffer);

    this.tempZipPath = zipPath;
    console.log(`Downloaded to: ${zipPath}`);
    return zipPath;
  }

  /**
   * Cleanup temp files
   */
  cleanup() {
    if (this.tempDir && fs.existsSync(this.tempDir)) {
      fs.rmSync(this.tempDir, { recursive: true, force: true });
      console.log(`Cleaned up temp directory: ${this.tempDir}`);
      this.tempDir = null;
    }

    if (this.tempZipPath && fs.existsSync(this.tempZipPath)) {
      fs.rmSync(this.tempZipPath, { force: true });
      console.log(`Cleaned up temp zip: ${this.tempZipPath}`);
      this.tempZipPath = null;
    }
  }
}

/**
 * CLI command handler
 */
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (!command) {
    console.log('Usage:');
    console.log('  node src/index.js analyze <input> [--output <file>] [--mode <quick|full|deep>] [--llm-timeout <ms>] [--label-llm-assist] [--flowchart <file.md>]');
    console.log('  node src/index.js batch-analyze <folder> [--output <folder>] [--concurrency <n>] [--label-llm-assist]');
    process.exit(1);
  }
  
  const options = parseArgs(args);
  const analyzer = new SkillFCGAnalyzer({
    llmProvider: process.env.LLM_PROVIDER || 'openai',
    llmModel: process.env.LLM_MODEL || 'gpt-5.5',
    llmApiKey: process.env.LLM_API_KEY || '',
    llmTimeout: Number(options.llmTimeout || process.env.LLM_TIMEOUT || 180000),
    llmEndpoint: process.env.LLM_ENDPOINT || '',
    mode: options.mode || 'full',
    semanticLlm: true,
    labelLlmAssist: options.labelLlmAssist || false,
    labelLlmConcurrency: options.labelLlmConcurrency || 2,
    labelLlmCache: options.labelLlmCache || ''
  });
  
  try {
    if (command === 'analyze') {
      const input = args[1];
      if (!input) {
        console.error('Error: Input path or URL required');
        process.exit(1);
      }
      
      const result = isHttpUrl(input)
        ? await analyzer.analyzeFromUrl(input)
        : await analyzer.analyze(input);
      
      if (options.output) {
        saveToJson(result, options.output);
        const flowPaths = deriveFlowchartPaths(options.output, options.flowchart || '');
        saveFlowchartArtifacts(result, flowPaths.markdownPath, flowPaths.mermaidPath);
      } else {
        console.log(JSON.stringify(result, null, 2));
      }
      
    } else if (command === 'batch-analyze') {
      const folder = args[1];
      if (!folder) {
        console.error('Error: Folder path required');
        process.exit(1);
      }
      
      await batchAnalyze(folder, options.output || './results', analyzer, options.concurrency || 4);
      
    } else {
      console.error(`Unknown command: ${command}`);
      process.exit(1);
    }
  } catch (error) {
    console.error(`Fatal error: ${error.message}`);
    process.exit(1);
  }
}

/**
 * Parse command line arguments
 * @param {Array} args - Command line arguments
 * @returns {Object} Parsed options
 */
function parseArgs(args) {
  const options = {
    semanticLlm: true,
    labelLlmAssist: false
  };
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--output' && i + 1 < args.length) {
      options.output = args[i + 1];
      i++;
    } else if (args[i] === '--mode' && i + 1 < args.length) {
      options.mode = args[i + 1];
      i++;
    } else if (args[i] === '--concurrency' && i + 1 < args.length) {
      options.concurrency = Number(args[i + 1]);
      i++;
    } else if (args[i] === '--llm-timeout' && i + 1 < args.length) {
      options.llmTimeout = Number(args[i + 1]);
      i++;
    } else if (args[i] === '--label-llm-assist') {
      options.labelLlmAssist = true;
    } else if (args[i] === '--label-llm-concurrency' && i + 1 < args.length) {
      options.labelLlmConcurrency = Number(args[i + 1]);
      i++;
    } else if (args[i] === '--label-llm-cache' && i + 1 < args.length) {
      options.labelLlmCache = args[i + 1];
      i++;
    } else if (args[i] === '--flowchart' && i + 1 < args.length) {
      options.flowchart = args[i + 1];
      i++;
    } else if (String(args[i]).startsWith('--')) {
      throw new Error(`Unknown option: ${args[i]}`);
    }
  }
  
  return options;
}

/**
 * Batch analyze multiple skills
 * @param {string} folder - Folder containing skills
 * @param {string} outputFolder - Output folder
 * @param {SkillFCGAnalyzer} analyzer - Analyzer instance
 */
async function batchAnalyze(folder, outputFolder, analyzer, concurrency = 4) {
  if (!fs.existsSync(outputFolder)) {
    fs.mkdirSync(outputFolder, { recursive: true });
  }
  
  const outputRoot = path.resolve(outputFolder);
  const entries = fs.readdirSync(folder);
  const skills = entries.filter(entryName => {
    const fullPath = path.resolve(path.join(folder, entryName));

    // Never analyze output directory itself.
    if (fullPath === outputRoot) {
      return false;
    }

    if (entryName.endsWith('.zip')) {
      return true;
    }

    if (!fs.statSync(fullPath).isDirectory()) {
      return false;
    }

    // Skip hidden/system directories and dependency folders.
    if (entryName.startsWith('.') || entryName === 'node_modules') {
      return false;
    }

    // Directory is considered a skill only when SKILL.md exists.
    return fs.existsSync(path.join(fullPath, 'SKILL.md'));
  });
  
  console.log(`Found ${skills.length} skills to analyze`);

  const queue = [...skills];
  const workerCount = Math.max(1, Math.min(concurrency, skills.length || 1));

  const workers = Array.from({ length: workerCount }, async () => {
    const workerAnalyzer = new SkillFCGAnalyzer({
      llmProvider: analyzer.llmProvider,
      llmModel: analyzer.llmModel,
      llmApiKey: analyzer.llmApiKey,
      llmTimeout: analyzer.llmTimeout,
      llmEndpoint: analyzer.llmEndpoint,
      mode: analyzer.mode,
      semanticLlm: analyzer.semanticLlm,
      semanticGateBatchSize: analyzer.semanticGateBatchSize,
      semanticGateConcurrency: analyzer.semanticGateConcurrency,
      semanticGateMaxBatchChars: analyzer.semanticGateMaxBatchChars,
      semanticGateCache: analyzer.semanticGateCache,
      labelLlmAssist: analyzer.labelLlmAssist,
      labelLlmConcurrency: analyzer.labelLlmConcurrency,
      labelLlmCache: analyzer.labelLlmCache,
      maxDependencyCandidates: analyzer.maxDependencyCandidates,
      dependencyLlmPolicy: analyzer.dependencyLlmPolicy,
      dependencyLlmMaxPairs: analyzer.dependencyLlmMaxPairs,
      dependencyLlmBatchSize: analyzer.dependencyLlmBatchSize,
      dependencyLlmCache: analyzer.dependencyLlmCache
    });

    while (queue.length > 0) {
      const skill = queue.shift();
      if (!skill) break;

      const inputPath = path.join(folder, skill);
      const outputPath = path.join(outputFolder, `${path.parse(skill).name}-fcg.json`);

      try {
        console.log(`\nAnalyzing: ${skill}`);
        const result = await workerAnalyzer.analyze(inputPath);
        saveToJson(result, outputPath);
        const flowPaths = deriveFlowchartPaths(outputPath);
        saveFlowchartArtifacts(result, flowPaths.markdownPath, flowPaths.mermaidPath);
      } catch (error) {
        console.error(`Failed to analyze ${skill}: ${error.message}`);
      }
    }
  });

  await Promise.all(workers);
  console.log('\nBatch analysis completed');
}

function isHttpUrl(value) {
  return /^https?:\/\//i.test(value || '');
}

function sanitizeFileName(value) {
  return String(value || 'skill').replace(/[^\w.-]+/g, '-');
}

function isZipPayload(url, contentType) {
  if (/\.zip(?:$|\?)/i.test(url)) return true;
  return (
    contentType.includes('application/zip') ||
    contentType.includes('application/x-zip-compressed') ||
    contentType.includes('application/octet-stream')
  );
}

function resolveZipUrl(baseUrl, html) {
  const linkMatches = [];
  const hrefRegex = /href\s*=\s*["']([^"']+)["']/gi;
  let match;

  while ((match = hrefRegex.exec(html)) !== null) {
    linkMatches.push(match[1]);
  }

  const prioritized = linkMatches.find(href => /\.zip(?:$|\?)/i.test(href));
  if (prioritized) return new URL(prioritized, baseUrl).toString();

  const secondary = linkMatches.find(href => /download/i.test(href));
  if (secondary) return new URL(secondary, baseUrl).toString();

  if (/clawhub\.ai/i.test(baseUrl)) {
    return `${baseUrl.replace(/\/+$/, '')}/download`;
  }

  return null;
}

async function fetchWithTimeout(fetchFn, url, timeoutMs) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetchFn(url, {
      redirect: 'follow',
      signal: controller.signal
    });
  } finally {
    clearTimeout(timeout);
  }
}




function buildLegacyDebugOutputs() {
  return {
    sourceSink: { sources: [], sinks: [] },
    pathCompression: { exact_path_count: 0, compression_nodes: [], compression_edges: [], source_sink_pairs: [] },
    paths: []
  };
}

function buildDeepModeEdges(tools) {
  const sortableTools = tools
    .map(tool => ({
      tool,
      file: String(tool.location?.file || ''),
      line: Number(tool.location?.line || 0)
    }))
    .sort((a, b) => {
      if (a.file !== b.file) {
        if (a.file === 'SKILL.md') return -1;
        if (b.file === 'SKILL.md') return 1;
        if (a.file === 'README.md') return -1;
        if (b.file === 'README.md') return 1;
        return a.file.localeCompare(b.file);
      }
      return a.line - b.line;
    });

  const edges = [];
  for (let i = 0; i < sortableTools.length - 1; i++) {
    const current = sortableTools[i].tool;
    const next = sortableTools[i + 1].tool;
    if (!current?.name || !next?.name || current.name === next.name) {
      continue;
    }

    edges.push({
      id: `deep_edge_${edges.length + 1}`,
      source: current.name,
      target: next.name,
      type: 'control_flow',
      confidence: 0.35,
      validation_method: 'structural',
      data_flow: {
        from_param: 'context',
        to_param: 'context',
        data_type: 'object'
      },
      semantic_reason: 'Deep mode structural sequence edge'
    });
  }

  return edges;
}

// Sum two semantic-gate usage summaries (doc-flow gate + constraint-endpoint
// resolution) into one, recomputing the cache-hit ratio over the combined
// prompt tokens. Either operand may be null.
function mergeSemanticGateUsage(a, b) {
  if (!a) return b || null;
  if (!b) return a;
  const calls = (a.calls || 0) + (b.calls || 0);
  const prompt_tokens = (a.prompt_tokens || 0) + (b.prompt_tokens || 0);
  const completion_tokens = (a.completion_tokens || 0) + (b.completion_tokens || 0);
  const total_tokens = (a.total_tokens || 0) + (b.total_tokens || 0);
  const cached_tokens = (a.cached_tokens || 0) + (b.cached_tokens || 0);
  return {
    calls,
    prompt_tokens,
    completion_tokens,
    total_tokens,
    cached_tokens,
    prompt_cache_hit_ratio: prompt_tokens ? Math.round((cached_tokens / prompt_tokens) * 1000) / 1000 : 0
  };
}

function shouldAddImplicitToolToLlmEdge(tool) {
  if (!tool || !tool.name) return false;
  if (tool.callsite_id) return false;
  if (tool.excludeFromImplicitLlmEdge) return false;
  if (tool.excludeFromTypeAnalysis) return false;
  if (tool.name.startsWith('doc.')) return false;
  if (tool.name.startsWith('rule.')) return false;
  return true;
}

function limitDocumentFlow(documentFlow = {}, maxNodes = 80) {
  const nodes = documentFlow.nodes || [];
  const edges = documentFlow.edges || [];
  if (!Number.isInteger(maxNodes) || maxNodes <= 0 || nodes.length <= maxNodes) {
    return { nodes, edges, truncated: false };
  }

  const keptNodes = nodes.slice(0, maxNodes);
  const allowed = new Set();
  for (const node of keptNodes) {
    if (node.id) allowed.add(node.id);
    if (node.name) allowed.add(node.name);
  }
  allowed.add('user.query');
  allowed.add('llm.inference');

  return {
    nodes: keptNodes,
    edges: edges.filter(edge => allowed.has(edge.source) && allowed.has(edge.target)),
    truncated: true
  };
}

function limitMediation(mediation = {}, existingTools = [], maxNodes = 0) {
  const nodes = mediation.nodes || [];
  const edges = mediation.edges || [];
  if (!Number.isInteger(maxNodes) || maxNodes <= 0 || nodes.length <= maxNodes) {
    return { nodes, edges, truncated: false };
  }

  const keptNodes = nodes.slice(0, maxNodes);
  const allowed = new Set((existingTools || []).map(tool => tool.name).filter(Boolean));
  for (const node of keptNodes) {
    if (node.name) allowed.add(node.name);
  }

  return {
    nodes: keptNodes,
    edges: edges.filter(edge => allowed.has(edge.source) && allowed.has(edge.target)),
    truncated: true
  };
}

function compareSemanticPairPriority(a, b) {
  const priorityDelta = semanticPairPriority(a) - semanticPairPriority(b);
  if (priorityDelta !== 0) return priorityDelta;

  const confidenceDelta = Number(b.confidence || 0) - Number(a.confidence || 0);
  if (confidenceDelta !== 0) return confidenceDelta;

  return semanticPairKey(a).localeCompare(semanticPairKey(b));
}

function semanticPairPriority(pair = {}) {
  const source = pair.source || {};
  const target = pair.target || {};
  const sourceName = String(source.name || '');
  const targetName = String(target.name || '');

  if (sourceName === 'user.query' && targetName === 'llm.inference') return 0;
  if (sourceName === 'user.query') return 1;
  if (targetName === 'llm.inference' || sourceName === 'llm.inference') return 2;
  if (sourceName.startsWith('llm.inference#') || targetName.startsWith('llm.inference#')) return 3;
  if (source.callsite_id || target.callsite_id) return 4;
  return 5;
}

function semanticPairKey(pair = {}) {
  return [
    pair?.source?.name || '',
    pair?.target?.name || '',
    pair?.compatibleParams?.[0]?.fromParam || '',
    pair?.compatibleParams?.[0]?.toParam || ''
  ].join('::');
}

function normalizePositiveInteger(value, fallback) {
  const number = Number(value);
  return Number.isInteger(number) && number > 0 ? number : fallback;
}

function normalizeNonNegativeInteger(value, fallback) {
  const number = Number(value);
  return Number.isInteger(number) && number >= 0 ? number : fallback;
}

function normalizeDependencyLlmPolicy(value) {
  const policy = String(value || '').trim().toLowerCase();
  if (['off', 'none', 'false', '0'].includes(policy)) return 'off';
  if (policy === 'all') return 'all';
  return 'high_value';
}

function isTruthyEnv(value) {
  return /^(1|true|yes|on)$/i.test(String(value || '').trim());
}

// True only for an EXPLICIT off value. An unset/empty var is NOT falsy, so a
// default-on flag (cycleExpand) stays on unless the operator explicitly opts out.
function isFalsyEnv(value) {
  return /^(0|false|no|off)$/i.test(String(value || '').trim());
}

function defaultLabelLlmCachePath(inputPath) {
  const base = path.basename(String(inputPath || 'skill'), path.extname(String(inputPath || 'skill'))) || 'skill';
  return path.join(os.tmpdir(), `skill-fcg-label-llm-${sanitizeFileName(base)}.jsonl`);
}

// Run CLI if executed directly
if (require.main === module) {
  main();
}

module.exports = {
  SkillFCGAnalyzer,
  batchAnalyze,
  parseArgs,
  saveToJson,
  saveFlowchartArtifacts,
  deriveFlowchartPaths
};


