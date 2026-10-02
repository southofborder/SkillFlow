#!/usr/bin/env node
/** Offline review-only CFG projection. Never executes Skill text or changes IR. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';

const FONT = 'Microsoft YaHei';
const FONT_SIZE = 18;
const CARD_WIDTH = 640;
const EDGE_WIDTH = 310;
const MARGIN = 40;
const GAP = 42;
const COUNT_NAMES = ['blocks', 'edges', 'instructions', 'inputs', 'outputs',
  'skill_constraints', 'block_constraints', 'instruction_constraints'];
const xml = value => String(value).replace(/[&<>"']/gu, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' })[c]);
const json = value => JSON.stringify(value);
const digest = value => createHash('sha256').update(value).digest('hex');

function argumentsFrom(argv) {
  const values = {};
  for (let i = 0; i < argv.length; i += 2) {
    const key = argv[i];
    if (!['--input', '--output-dir', '--audit', '--node-modules', '--browser', '--svg-output-dir'].includes(key)
      || !argv[i + 1] || values[key]) throw new Error(`Invalid argument: ${key}`);
    values[key] = argv[i + 1];
  }
  for (const key of ['--input', '--output-dir', '--audit', '--node-modules']) {
    if (!values[key]) throw new Error(`Required argument: ${key}`);
  }
  return values;
}

function operandText(operand) {
  if (operand.type === 'literal') return `literal: ${json(operand.literal_value)}`;
  let text = `${operand.type}: ${operand.identifier}`;
  if (operand.semantic_name != null) text += ` | ${operand.semantic_name}`;
  return text;
}

function rawCounts(cfg) {
  const counts = Object.fromEntries(COUNT_NAMES.map(name => [name, 0]));
  counts.blocks = Object.keys(cfg.blocks).length;
  counts.edges = cfg.edges.length;
  counts.skill_constraints = cfg.constraints.length;
  for (const block of Object.values(cfg.blocks)) {
    counts.block_constraints += block.constraints.length;
    for (const instruction of block.instructions) {
      counts.instructions++;
      counts.inputs += instruction.inputs.length;
      counts.outputs += instruction.outputs.length;
      counts.instruction_constraints += instruction.constraints.length;
    }
  }
  return counts;
}

function projection(sample) {
  const cfg = sample.cfg;
  if (!sample.basename || path.basename(sample.basename) !== sample.basename
    || /[<>:"/\\|?*\u0000-\u001f]/u.test(sample.basename)) {
    throw new Error(`Unsafe output basename: ${sample.basename}`);
  }
  const provenance = sample.provenance_lines ?? [];
  if (!Array.isArray(provenance) || provenance.some(line => typeof line !== 'string')) {
    throw new Error(`Invalid provenance lines: ${sample.sample_id}`);
  }
  let serial = 0;
  const item = (kind, text, bold = false, size = FONT_SIZE) => ({
    id: `text_${++serial}`, kind, text: String(text), bold, size,
  });
  const constraints = (values, kind, prefix) => values.length
    ? values.map((text, index) => item(kind, `${prefix}[${index}]: ${text}`))
    : [item(`${kind}_empty`, `${prefix}: []`)];
  if (sample.failure != null) {
    if (cfg !== null || ['reason', 'feedback_status', 'annotation_status'].some(
      key => typeof sample.failure[key] !== 'string' || !sample.failure[key].trim())) {
      throw new Error(`Failure card requires cfg=null and explicit reason/statuses: ${sample.sample_id}`);
    }
    return {
      kind: 'failure',
      header: { id: 'header', role: 'failure', width: 1180, items: [
        item('title', `${String(sample.index).padStart(3, '0')}  ${sample.skill_name}`, true, 27),
        item('failure_notice', `${sample.sample_id}  |  本轮无可用 CFG`, true, 24),
        item('failure_boundary', '这是执行状态卡，不是控制流图；未回退或冒充历史结果。', true, 20),
        ...provenance.map(line => item('provenance', line)),
        item('feedback_status', `反馈状态：${sample.failure.feedback_status}`),
        item('annotation_status', `标注状态：${sample.failure.annotation_status}`),
        item('failure_reason', `原因：${sample.failure.reason}`),
      ] },
      nodes: [], edges: [], counts: Object.fromEntries(COUNT_NAMES.map(name => [name, 0])),
    };
  }
  if (!cfg || typeof cfg.blocks !== 'object' || !Array.isArray(cfg.edges)
    || !Array.isArray(cfg.constraints) || !cfg.blocks[cfg.entry_block_id]) {
    throw new Error(`Invalid canonical CFG: ${sample.sample_id}`);
  }
  const header = {
    id: 'header', role: 'header', width: 1180,
    items: [
      item('title', `${String(sample.index).padStart(3, '0')}  ${sample.skill_name}`, true, 27),
      item('sample', `${sample.sample_id}  |  ${provenance.length ? `修复轮次 ${sample.repetition}` : `第 ${sample.repetition} 次`}  |  实际 CFG`, true, 20),
      ...provenance.map(line => item('provenance', line)),
      item('entry', `entry_block_id: ${cfg.entry_block_id}`),
      item('contexts', `declared_context_keys: ${json(cfg.declared_context_keys ?? [])}`),
      ...constraints(cfg.constraints, 'skill_constraints', 'Skill.constraints'),
    ],
  };
  const nodes = Object.entries(cfg.blocks).map(([id, block], index) => {
    if (block.block_id !== id || !Array.isArray(block.instructions)
      || !Array.isArray(block.constraints)) throw new Error(`Invalid block: ${id}`);
    const items = [
      item('block_title', `${id}${id === cfg.entry_block_id ? '  [入口]' : ''}`, true, 21),
      item('block_name', block.block_name, true, 20),
      item('source_kind', `data_source_kind: ${json(block.data_source_kind)}`),
      ...constraints(block.constraints, 'block_constraints', `${id}.constraints`),
    ];
    for (const instruction of block.instructions) {
      const start = items.length;
      items.push(item('instructions', `${instruction.id}  ${instruction.opcode}`, true, 20));
      for (const side of ['inputs', 'outputs']) {
        if (!instruction[side].length) items.push(item(`${side}_empty`, `${side}: []`));
        instruction[side].forEach((operand, operandIndex) => {
          items.push(item(side, `${side}[${operandIndex}]: ${operandText(operand)}`));
        });
      }
      items.push(...constraints(instruction.constraints, 'instruction_constraints',
        `${instruction.id}.constraints`));
      for (const line of items.slice(start)) line.ir_id = instruction.id;
    }
    return { id: `node_${index}`, raw_id: id, role: 'block', width: CARD_WIDTH,
      entry: id === cfg.entry_block_id, items };
  });
  const ids = new Map(nodes.map(node => [node.raw_id, node.id]));
  const edges = cfg.edges.map((edge, index) => {
    if (!ids.has(edge.source_block_id) || !ids.has(edge.target_block_id)) {
      throw new Error(`Edge endpoint not present: ${json(edge)}`);
    }
    return {
      id: `edge_${index + 1}`, role: 'edge_label', width: EDGE_WIDTH,
      source: ids.get(edge.source_block_id), target: ids.get(edge.target_block_id),
      source_block_id: edge.source_block_id, target_block_id: edge.target_block_id,
      items: [item('edge_id', `edge_${String(index + 1).padStart(3, '0')}`, true, 16),
        item('edge_condition', `condition_text: ${json(edge.condition_text ?? null)}`, false, 16)],
    };
  });
  return { kind: 'cfg', header, nodes, edges, counts: rawCounts(cfg) };
}

async function measure(page, cards) {
  return page.evaluate(async ({ cards, font }) => {
    await document.fonts.load(`18px "${font}"`);
    await document.fonts.ready;
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    return cards.map(card => {
      const padding = card.role === 'edge_label' ? 10 : 18;
      let cursor = padding;
      const items = card.items.map(item => {
        context.font = `${item.bold ? 700 : 400} ${item.size}px "${font}"`;
        const maxWidth = card.width - padding * 2 - 4;
        const lines = [];
        for (const paragraph of item.text.split(/\r\n|\r|\n/u)) {
          let line = '';
          for (const char of Array.from(paragraph)) {
            if (line && context.measureText(line + char).width > maxWidth) {
              // Prefer a nearby whitespace break, but also split unbroken IDs and URLs.
              const split = line.lastIndexOf(' ');
              if (split >= Math.floor(line.length * 0.55)) {
                lines.push(line.slice(0, split + 1));
                line = line.slice(split + 1) + char;
              } else { lines.push(line); line = char; }
            } else line += char;
          }
          lines.push(line);
        }
        const lineHeight = Math.ceil(item.size * 1.48);
        const measured = { ...item, lines, x: padding, y: cursor + item.size,
          line_height: lineHeight };
        cursor += lines.length * lineHeight + (item.bold ? 9 : 5);
        return measured;
      });
      return { ...card, items, height: Math.ceil(cursor + padding - 5) };
    });
  }, { cards, font: FONT });
}

function layoutGraph(viz, nodes, edges, spacing = 1) {
  const dot = [
    'digraph Review {',
    `graph [rankdir=TB, nodesep=${1.0 * spacing}, ranksep=${1.1 * spacing}, splines=spline, overlap=false, concentrate=false, ordering=out, outputorder=edgesfirst, margin=0, pad=0];`,
    'node [shape=box, fixedsize=true, label="", margin=0];',
    'edge [arrowsize=1.0];',
  ];
  for (const node of nodes) dot.push(`${node.id} [width=${node.width / 72}, height=${node.height / 72}];`);
  for (const edge of edges) {
    const label = `<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0" FIXEDSIZE="TRUE" WIDTH="${edge.width}" HEIGHT="${edge.height}"><TR><TD> </TD></TR></TABLE>`;
    dot.push(`${edge.source} -> ${edge.target} [id="${edge.id}", label=<${label}>];`);
  }
  dot.push('}');
  const layout = viz.renderJSON(dot.join('\n'), { engine: 'dot' });
  if (!layout.bb || layout.objects?.length !== nodes.length || (layout.edges?.length ?? 0) !== edges.length) {
    throw new Error('Graphviz did not preserve every original node and edge');
  }
  return layout;
}

function cardSvg(card, x, y) {
  const fill = card.role === 'failure' ? '#fff1f0' : card.role === 'edge_label' ? '#ffffff' : card.role === 'header' ? '#edf5f7' : '#fbfcfe';
  const stroke = card.role === 'failure' ? '#bb3e36' : card.entry ? '#007f86' : card.role === 'edge_label' ? '#d6e3e9' : '#829bad';
  const blockAttribute = card.role === 'block' ? ` data-block-id="${xml(card.raw_id)}"` : '';
  const parts = [`<g id="${card.id}" data-card="${card.role}"${blockAttribute} transform="translate(${x},${y})">`,
    `<rect data-card-bound="true" x="0" y="0" width="${card.width}" height="${card.height}" rx="9" fill="${fill}" stroke="${stroke}" stroke-width="${card.entry ? 3 : 1.2}"/>`];
  let activeInstruction = null;
  for (const item of card.items) {
    if ((item.ir_id ?? null) !== activeInstruction) {
      if (activeInstruction !== null) parts.push('</g>');
      activeInstruction = item.ir_id ?? null;
      if (activeInstruction !== null) parts.push(`<g id="ir-${xml(encodeURIComponent(activeInstruction))}" data-ir-id="${xml(activeInstruction)}" data-block-id="${xml(card.raw_id)}">`);
    }
    parts.push(`<text data-item="${item.id}" data-kind="${item.kind}" x="${item.x}" y="${item.y}" fill="${item.bold ? '#123c54' : '#263b47'}" font-family="${FONT}" font-size="${item.size}" font-weight="${item.bold ? 700 : 400}" xml:space="preserve">`);
    item.lines.forEach((line, index) => parts.push(`<tspan x="${item.x}" y="${item.y + index * item.line_height}">${xml(line)}</tspan>`));
    parts.push('</text>');
  }
  if (activeInstruction !== null) parts.push('</g>');
  parts.push('</g>');
  return parts.join('');
}

function svgFromLayout(layout, header, nodes, edges) {
  const [, , graphWidth, graphHeight] = layout.bb.split(',').map(Number);
  const top = MARGIN + header.height + GAP;
  const width = Math.ceil(Math.max(graphWidth, header.width) + MARGIN * 2);
  const height = Math.ceil(top + graphHeight + MARGIN);
  if (width > 32000 || height > 32000 || width * height > 180_000_000) {
    throw new Error(`Canvas ${width}x${height} exceeds review PNG limit; do not silently shrink text`);
  }
  const point = ([x, y]) => [x + MARGIN, top + graphHeight - y];
  const renderedEdges = [];
  for (const edge of layout.edges ?? []) {
    const original = edges.find(item => item.id === edge.id);
    if (!original || !edge.lp) throw new Error(`Missing original edge/label position: ${edge.id}`);
    const pieces = [`<g data-edge="${edge.id}" data-source="${xml(original.source_block_id)}" data-target="${xml(original.target_block_id)}">`];
    for (const operation of edge._draw_ ?? []) {
      if (operation.op !== 'b') continue;
      const points = operation.points.map(point);
      let d = `M ${points[0].join(' ')}`;
      for (let index = 1; index < points.length; index += 3) {
        d += ` C ${points.slice(index, index + 3).map(p => p.join(' ')).join(' ')}`;
      }
      pieces.push(`<path data-edge-line="${edge.id}" d="${d}" fill="none" stroke="#30798a" stroke-width="2.2"/>`);
    }
    for (const operation of edge._hdraw_ ?? []) {
      if (operation.op !== 'P') continue;
      pieces.push(`<polygon data-arrow="${edge.id}" points="${operation.points.map(point).map(p => p.join(',')).join(' ')}" fill="#30798a" stroke="#30798a"/>`);
    }
    pieces.push('</g>');
    renderedEdges.push(pieces.join(''));
  }
  const nodeCards = layout.objects.map(node => {
    const card = nodes.find(item => item.id === node.name);
    if (!card) throw new Error(`Unexpected layout node: ${node.name}`);
    const [x, y] = point(node.pos.split(',').map(Number));
    return cardSvg(card, x - card.width / 2, y - card.height / 2);
  });
  const labelCards = (layout.edges ?? []).map(edge => {
    const card = edges.find(item => item.id === edge.id);
    const [x, y] = point(edge.lp.split(',').map(Number));
    return cardSvg(card, x - card.width / 2, y - card.height / 2);
  });
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" style="display:block"><rect width="100%" height="100%" fill="white"/>${cardSvg(header, MARGIN, MARGIN)}${renderedEdges.join('')}${nodeCards.join('')}${labelCards.join('')}</svg>`;
  return { svg, width, height };
}

function failureDrawing(header) {
  const width = Math.ceil(header.width + MARGIN * 2);
  const height = Math.ceil(header.height + MARGIN * 2);
  if (width > 32000 || height > 32000 || width * height > 180_000_000) {
    throw new Error(`Failure canvas ${width}x${height} exceeds review PNG limit; do not truncate its explanation`);
  }
  return { width, height,
    svg: `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" style="display:block"><rect width="100%" height="100%" fill="white"/>${cardSvg(header, MARGIN, MARGIN)}</svg>` };
}

async function settleEdgeLabels(page, width, height) {
  // Graphviz reserves label space, but curved splines can still graze that space.
  // Move only display labels into the nearest clear space; control-flow paths,
  // endpoints, IDs and conditions remain unchanged.
  return page.evaluate(({ width, height }) => {
    const readBox = element => {
      const r = element.getBoundingClientRect();
      return { x: r.x, y: r.y, width: r.width, height: r.height };
    };
    const boxes = [...document.querySelectorAll('[data-card]')].map(group => ({
      id: group.id, group, role: group.dataset.card,
      ...readBox(group.querySelector('[data-card-bound]')),
    }));
    const buckets = new Map();
    const cell = 64;
    for (const curve of document.querySelectorAll('[data-edge-line]')) {
      const length = curve.getTotalLength();
      for (let distance = 0; distance <= length; distance += 3) {
        const p = curve.getPointAtLength(distance);
        const key = `${Math.floor(p.x / cell)},${Math.floor(p.y / cell)}`;
        if (!buckets.has(key)) buckets.set(key, []);
        buckets.get(key).push(p);
      }
    }
    const overlaps = (a, b) => a.x < b.x + b.width + 4 && a.x + a.width + 4 > b.x
      && a.y < b.y + b.height + 4 && a.y + a.height + 4 > b.y;
    const clear = (candidate, id) => {
      if (candidate.x < 8 || candidate.y < 8 || candidate.x + candidate.width > width - 8
        || candidate.y + candidate.height > height - 8) return false;
      if (boxes.some(box => box.id !== id && overlaps(candidate, box))) return false;
      for (let x = Math.floor((candidate.x - 3) / cell); x <= Math.floor((candidate.x + candidate.width + 3) / cell); x++) {
        for (let y = Math.floor((candidate.y - 3) / cell); y <= Math.floor((candidate.y + candidate.height + 3) / cell); y++) {
          if ((buckets.get(`${x},${y}`) ?? []).some(p => p.x > candidate.x - 3
            && p.x < candidate.x + candidate.width + 3 && p.y > candidate.y - 3
            && p.y < candidate.y + candidate.height + 3)) return false;
        }
      }
      return true;
    };
    const offsets = [];
    for (let dx = -360; dx <= 360; dx += 12) {
      for (let dy = -240; dy <= 240; dy += 12) offsets.push({ dx, dy });
    }
    offsets.sort((a, b) => a.dx ** 2 + a.dy ** 2 - b.dx ** 2 - b.dy ** 2);
    const shifts = [];
    for (const box of boxes.filter(item => item.role === 'edge_label')) {
      if (clear(box, box.id)) continue;
      const offset = offsets.find(({ dx, dy }) => clear({ ...box, x: box.x + dx, y: box.y + dy }, box.id));
      if (!offset) continue; // Audit rejects this layout; caller tries wider spacing.
      box.x += offset.dx;
      box.y += offset.dy;
      box.group.setAttribute('transform', `translate(${box.x},${box.y})`);
      shifts.push({ edge: box.id, dx: offset.dx, dy: offset.dy });
    }
    return { shifts, svg: document.querySelector('svg').outerHTML };
  }, { width, height });
}

async function inspectRendered(page, cards, counts, expectedEdges, width, height) {
  return page.evaluate(async ({ cards, counts, expectedEdges, width, height, countNames }) => {
    await document.fonts.ready;
    const norm = value => String(value).replace(/\s+/gu, '');
    const rect = element => {
      const box = element.getBoundingClientRect();
      return { x: box.x, y: box.y, width: box.width, height: box.height };
    };
    const within = (child, parent, epsilon = 1.1) => child.x >= parent.x - epsilon
      && child.y >= parent.y - epsilon
      && child.x + child.width <= parent.x + parent.width + epsilon
      && child.y + child.height <= parent.y + parent.height + epsilon;
    const intersects = (a, b, padding = 1.5) => a.x + a.width - padding > b.x + padding
      && b.x + b.width - padding > a.x + padding
      && a.y + a.height - padding > b.y + padding
      && b.y + b.height - padding > a.y + padding;
    const textChecks = [];
    const boundsChecks = [];
    const identityChecks = [];
    const instructionLocations = [];
    const blockLocations = [];
    const actualCounts = Object.fromEntries(countNames.map(name => [name, 0]));
    actualCounts.blocks = document.querySelectorAll('[data-card="block"]').length;
    actualCounts.edges = document.querySelectorAll('[data-edge]').length;
    const cardBoxes = [];
    for (const card of cards) {
      const group = document.getElementById(card.id);
      if (!group) throw new Error(`Missing rendered card ${card.id}`);
      const box = rect(group.querySelector('[data-card-bound]'));
      if (card.role === 'block') {
        identityChecks.push({ kind: 'block_id', block_id: card.raw_id,
          passed: group.dataset.blockId === card.raw_id });
        blockLocations.push({ block_id: card.raw_id, ...box });
        const operations = [...group.querySelectorAll('[data-ir-id]')];
        for (const instruction of card.items.filter(item => item.kind === 'instructions')) {
          const matches = operations.filter(element => element.dataset.irId === instruction.ir_id);
          const operation = matches[0];
          identityChecks.push({ kind: 'instruction_id', instruction_id: instruction.ir_id,
            block_id: card.raw_id, passed: matches.length === 1 && operation.dataset.blockId === card.raw_id });
          if (operation) instructionLocations.push({ instruction_id: instruction.ir_id,
            block_id: card.raw_id, ...rect(operation) });
        }
      }
      cardBoxes.push({ id: card.id, role: card.role, ...box });
      boundsChecks.push({ id: card.id, kind: 'card_on_canvas', ...box,
        passed: within(box, { x: 0, y: 0, width, height }) });
      for (const item of card.items) {
        const element = group.querySelector(`[data-item="${item.id}"]`);
        const actual = element?.textContent ?? '';
        const passed = Boolean(element) && norm(actual) === norm(item.text);
        textChecks.push({ id: item.id, card: card.id, kind: item.kind, expected: item.text,
          rendered: actual, passed });
        if (!element) continue;
        if (Object.hasOwn(actualCounts, item.kind)) actualCounts[item.kind]++;
        const boxText = rect(element);
        boundsChecks.push({ id: item.id, card: card.id, kind: 'text_in_card', ...boxText,
          passed: within(boxText, box) });
        for (const line of element.querySelectorAll('tspan')) {
          boundsChecks.push({ id: item.id, card: card.id, kind: 'line_in_card',
            ...rect(line), passed: within(rect(line), box) });
        }
      }
    }
    const collisions = [];
    for (let first = 0; first < cardBoxes.length; first++) {
      for (let second = first + 1; second < cardBoxes.length; second++) {
        if (intersects(cardBoxes[first], cardBoxes[second])) {
          collisions.push({ kind: 'card_overlap', first: cardBoxes[first].id,
            second: cardBoxes[second].id });
        }
      }
    }
    // Inspect actual SVG curve points, not only requested layout geometry.
    for (const edgePath of document.querySelectorAll('[data-edge-line]')) {
      const length = edgePath.getTotalLength();
      for (let distance = 0; distance <= length; distance += 5) {
        const p = edgePath.getPointAtLength(distance);
        for (const box of cardBoxes) {
          if (p.x > box.x + 3 && p.x < box.x + box.width - 3
            && p.y > box.y + 3 && p.y < box.y + box.height - 3) {
            collisions.push({ kind: 'edge_crosses_card', edge: edgePath.dataset.edgeLine,
              card: box.id, x: p.x, y: p.y });
            distance = length + 1;
            break;
          }
        }
      }
      boundsChecks.push({ id: edgePath.dataset.edgeLine, kind: 'edge_on_canvas',
        ...rect(edgePath), passed: within(rect(edgePath), { x: 0, y: 0, width, height }) });
    }
    for (const arrow of document.querySelectorAll('[data-arrow]')) {
      boundsChecks.push({ id: arrow.dataset.arrow, kind: 'arrow_on_canvas',
        ...rect(arrow), passed: within(rect(arrow), { x: 0, y: 0, width, height }) });
    }
    const edgeChecks = expectedEdges.map(edge => {
      const group = document.querySelector(`[data-edge="${edge.id}"]`);
      return { edge: edge.id, source: edge.source_block_id, target: edge.target_block_id,
        passed: Boolean(group) && group.dataset.source === edge.source_block_id
          && group.dataset.target === edge.target_block_id
          && group.querySelectorAll('[data-edge-line]').length > 0
          && group.querySelectorAll('[data-arrow]').length > 0 };
    });
    const countsPassed = countNames.every(name => counts[name] === actualCounts[name]);
    const actualTextCount = document.querySelectorAll('svg text').length;
    return {
      rendered_counts: actualCounts,
      counts_checks_passed: countsPassed,
      identity_checks_passed: identityChecks.every(item => item.passed)
        && document.querySelectorAll('[data-ir-id]').length === counts.instructions,
      identity_checks: identityChecks, instruction_locations: instructionLocations,
      block_locations: blockLocations,
      text_checks_passed: textChecks.every(item => item.passed)
        && actualTextCount === textChecks.length && edgeChecks.every(item => item.passed),
      bounds_checks_passed: boundsChecks.every(item => item.passed) && collisions.length === 0,
      text_checks: textChecks, bounds_checks: boundsChecks, edge_checks: edgeChecks,
      collisions, rendered_text_count: actualTextCount,
    };
  }, { cards, counts, expectedEdges, width, height, countNames: COUNT_NAMES });
}

async function main() {
  const args = argumentsFrom(process.argv.slice(2));
  const require = createRequire(path.join(path.resolve(args['--node-modules']), '_review-loader.cjs'));
  const vizModule = require('@viz-js/viz');
  const { chromium } = require('playwright');
  const sharp = require('sharp');
  const inputBytes = await fs.readFile(args['--input']);
  const input = JSON.parse(inputBytes.toString('utf8'));
  if (!Array.isArray(input.samples) || !input.samples.length) throw new Error('samples must be nonempty');
  if (new Set(input.samples.map(sample => sample.basename)).size !== input.samples.length) {
    throw new Error('Duplicate output basenames');
  }
  const executablePath = args['--browser']
    ?? 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
  await fs.access(executablePath);
  await fs.mkdir(args['--output-dir'], { recursive: true });
  if (args['--svg-output-dir']) await fs.mkdir(args['--svg-output-dir'], { recursive: true });
  await fs.mkdir(path.dirname(path.resolve(args['--audit'])), { recursive: true });
  const audit = { schema_version: 1, renderer: 'Graphviz WASM fixed measured cards + browser SVG',
    graphviz_version: vizModule.graphvizVersion, font: FONT, body_font_px: FONT_SIZE,
    input_sha256: digest(inputBytes), samples: [], status: 'running' };
  const writeAudit = () => fs.writeFile(args['--audit'], JSON.stringify(audit, null, 2) + '\n');
  const browser = await chromium.launch({ executablePath, headless: true,
    args: ['--disable-background-networking', '--disable-component-update', '--no-first-run'] });
  try {
    const context = await browser.newContext({ viewport: { width: 1280, height: 960 },
      deviceScaleFactor: 1, serviceWorkers: 'block', offline: true });
    await context.route('**/*', route => route.abort());
    const page = await context.newPage();
    const viz = await vizModule.instance();
    for (const sample of input.samples) {
      const model = projection(sample);
      await page.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0"></body></html>');
      const measured = await measure(page, [model.header, ...model.nodes, ...model.edges]);
      const header = measured[0];
      const nodes = measured.slice(1, 1 + model.nodes.length);
      const edges = measured.slice(1 + model.nodes.length);
      let drawing, inspection, selectedSpacing, labelPlacement;
      for (const spacing of model.kind === 'failure' ? [null] : [1, 1.6, 2.4]) {
        drawing = model.kind === 'failure' ? failureDrawing(header)
          : svgFromLayout(layoutGraph(viz, nodes, edges, spacing), header, nodes, edges);
        await page.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;padding:0;background:white}body{width:${drawing.width}px;height:${drawing.height}px}*{box-sizing:border-box}</style></head><body>${drawing.svg}</body></html>`);
        labelPlacement = await settleEdgeLabels(page, drawing.width, drawing.height);
        drawing.svg = labelPlacement.svg;
        inspection = await inspectRendered(page, measured, model.counts, model.edges,
          drawing.width, drawing.height);
        selectedSpacing = spacing;
        if (inspection.text_checks_passed && inspection.counts_checks_passed && inspection.identity_checks_passed
          && inspection.bounds_checks_passed) break;
      }
      const record = { index: sample.index, sample_id: sample.sample_id, basename: sample.basename,
        kind: model.kind, provenance_lines: sample.provenance_lines ?? [],
        repetition: sample.repetition, run_id: sample.run_id, analysis_sha256: sample.analysis_sha256,
        counts: model.counts, width: drawing.width, height: drawing.height,
        layout_spacing: selectedSpacing, label_position_adjustments: labelPlacement.shifts,
        svg_sha256: digest(drawing.svg), ...inspection };
      audit.samples.push(record);
      if (!inspection.text_checks_passed || !inspection.counts_checks_passed || !inspection.bounds_checks_passed || !inspection.identity_checks_passed) {
        await writeAudit();
        throw new Error(`${sample.sample_id}: rendered audit failed: ${JSON.stringify({
          text: inspection.text_checks_passed, counts: inspection.counts_checks_passed,
          bounds: inspection.bounds_checks_passed, identities: inspection.identity_checks_passed,
          collisions: inspection.collisions.slice(0, 8),
          failed_bounds: inspection.bounds_checks.filter(item => !item.passed).slice(0, 4),
        })}`);
      }
      // fullPage screenshots are at least as large as the viewport. Narrow or
      // short diagrams must therefore reduce the viewport before capture.
      await page.setViewportSize({ width: Math.min(1280, drawing.width),
        height: Math.min(960, drawing.height) });
      const png = await page.screenshot({ fullPage: true, type: 'png', timeout: 120000 });
      const metadata = await sharp(png).metadata();
      if (metadata.width !== drawing.width || metadata.height !== drawing.height) {
        throw new Error(`${sample.sample_id}: screenshot dimensions ${metadata.width}x${metadata.height} differ from SVG canvas ${drawing.width}x${drawing.height}`);
      }
      const output = path.join(args['--output-dir'], `${sample.basename}.png`);
      await fs.writeFile(output, png);
      if (args['--svg-output-dir']) {
        await fs.writeFile(path.join(args['--svg-output-dir'], `${sample.basename}.svg`), drawing.svg);
      }
      record.png_sha256 = digest(png);
      record.png_bytes = png.length;
      record.png_dimensions_checked = true;
      await writeAudit();
      console.log(`${sample.sample_id}: ${drawing.width}x${drawing.height}; ${model.counts.blocks} blocks, ${model.counts.edges} edges; audit passed`);
    }
    audit.status = 'passed';
    await writeAudit();
  } catch (error) {
    audit.status = 'failed';
    audit.error = String(error.message ?? error);
    await writeAudit();
    throw error;
  } finally { await browser.close(); }
}

main().catch(error => { console.error(error.stack ?? error); process.exitCode = 1; });
