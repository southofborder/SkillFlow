/**
 * Shared shell-command classifier.
 *
 * Both the Markdown code-block path (doc-flow-extractor) and the tool-extractor
 * bash-block path use this so command-level operation typing never drifts
 * between the two. Given a raw shell command line, it splits compound commands
 * and classifies each into an FCG operation_type with concrete targets
 * (URLs for egress, file paths for read/write).
 *
 * Deterministic and rule-only: no LLM. This is the fix for defect (1) — code
 * blocks (e.g. weather's `curl "wttr.in/..."`) were dropped wholesale before.
 */

// Command-name based classification. Ordered by specificity.
const EGRESS_COMMANDS = new Set(['curl', 'wget', 'http', 'https', 'httpie', 'nc', 'ncat', 'telnet', 'ssh', 'scp', 'rsync', 'ftp', 'sftp']);
const EXEC_COMMANDS = new Set(['bash', 'sh', 'zsh', 'node', 'python', 'python3', 'ruby', 'perl', 'php', 'deno', 'bun', 'npx', 'pnpm', 'yarn', 'npm', 'pip', 'pip3', 'make', 'docker', 'kubectl', 'git']);
const READ_COMMANDS = new Set(['cat', 'less', 'more', 'head', 'tail', 'grep', 'rg', 'find', 'ls', 'stat', 'read', 'awk', 'sed', 'jq']);
const WRITE_COMMANDS = new Set(['tee', 'touch', 'mkdir', 'cp', 'mv', 'rm', 'chmod', 'chown', 'ln', 'dd']);

const URL_REGEX = /\bhttps?:\/\/[^\s"'`)]+/gi;
// Bare host used with a network tool, e.g. curl "wttr.in/London". Captures the host.
const BARE_HOST_REGEX = /["']?([a-z0-9](?:[a-z0-9-]*[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)+)(?:\/[^\s"'`]*)?["']?/gi;
const REDIRECT_FILE_REGEX = />>?\s*("?[~./\w-]+(?:\/[~./\w-]+)*\.\w+"?|"?\/dev\/[\w/]+"?)/g;
const FILE_PATH_REGEX = /("?(?:\.{0,2}\/)?[\w-]+(?:\/[\w.-]+)*\.[a-z0-9]{1,6}"?)/gi;

/**
 * Split a shell command line into individual command segments.
 * Handles pipes, &&, ||, ; separators. Respects nothing fancy (no full parse);
 * good enough for doc example commands.
 * @param {string} line
 * @returns {Array<string>}
 */
function splitCommandSegments(line) {
  return String(line || '')
    .split(/\|{1,2}|&&|;|\band\b(?=\s)/g)
    .map(seg => seg.trim())
    .filter(Boolean);
}

/**
 * Return the leading command name for a single segment, skipping env-var
 * assignments (FOO=bar cmd), sudo/command/builtin wrappers, and redirections.
 * @param {string} segment
 * @returns {string}
 */
function segmentCommandName(segment) {
  let rest = String(segment || '').trim();
  // Strip leading control keywords.
  rest = rest.replace(/^(?:if|then|do|while|until|for|else|elif)\s+/, '');
  // Strip leading VAR=value assignments.
  while (/^[A-Za-z_][A-Za-z0-9_]*=(?:"[^"]*"|'[^']*'|\S*)\s+/.test(rest)) {
    rest = rest.replace(/^[A-Za-z_][A-Za-z0-9_]*=(?:"[^"]*"|'[^']*'|\S*)\s+/, '');
  }
  const parts = rest.split(/\s+/).filter(Boolean);
  if (!parts.length) return '';
  let idx = 0;
  while (idx < parts.length && /^(?:sudo|command|builtin|exec|time|env)$/.test(parts[idx])) {
    idx += 1;
  }
  const name = parts[idx] || '';
  return name.replace(/^['"]|['"]$/g, '').replace(/^\\/, '');
}

/**
 * Extract URL / host / file targets referenced by a command segment.
 * @param {string} segment
 * @param {string} operationType
 * @returns {Array<{type: string, value: string, raw: string}>}
 */
function extractCommandTargets(segment, operationType) {
  const text = String(segment || '');
  const targets = [];
  const seen = new Set();

  const push = (type, value, raw) => {
    const cleaned = String(value || '').replace(/^['"]|['"]$/g, '').trim();
    if (!cleaned) return;
    const key = `${type}:${cleaned}`;
    if (seen.has(key)) return;
    seen.add(key);
    targets.push({ type, value: cleaned, raw: String(raw || cleaned).trim() });
  };

  if (operationType === 'external_egress') {
    let m;
    URL_REGEX.lastIndex = 0;
    let matchedUrl = false;
    while ((m = URL_REGEX.exec(text)) !== null) {
      matchedUrl = true;
      push('url', hostFromUrl(m[0]), m[0]);
    }
    if (!matchedUrl) {
      BARE_HOST_REGEX.lastIndex = 0;
      while ((m = BARE_HOST_REGEX.exec(text)) !== null) {
        const host = m[1];
        // Skip things that look like filenames rather than hosts.
        if (/\.(?:md|json|txt|log|sh|js|ts|png|jpg|csv|yml|yaml)$/i.test(host)) continue;
        push('url', host, m[0]);
      }
    }
  }

  if (operationType === 'write') {
    let m;
    REDIRECT_FILE_REGEX.lastIndex = 0;
    while ((m = REDIRECT_FILE_REGEX.exec(text)) !== null) {
      push('file', m[1], m[0]);
    }
  }

  if (operationType === 'read' || operationType === 'write') {
    let m;
    FILE_PATH_REGEX.lastIndex = 0;
    while ((m = FILE_PATH_REGEX.exec(text)) !== null) {
      push('file', m[1], m[1]);
    }
  }

  return targets;
}

function hostFromUrl(url) {
  const match = String(url || '').match(/^https?:\/\/([^/\s"'`]+)/i);
  return match ? match[1] : String(url || '');
}

/**
 * Classify a single shell command line into one or more operation descriptors.
 * Returns [] for lines that carry no runtime action (comments, output echoes
 * of non-actionable text, pure control keywords).
 *
 * @param {string} line
 * @returns {Array<{command:string, operationType:string, targets:Array, segment:string}>}
 */
function classifyShellCommandLine(line) {
  const raw = String(line || '');
  const trimmed = stripInlineComment(raw).trim();
  if (!trimmed) return [];
  // Pure comment / shebang / control terminators.
  if (/^#/.test(trimmed) || /^#!/.test(raw.trim())) return [];
  if (/^(?:then|do|fi|done|else|elif|esac|;;)\b/.test(trimmed)) return [];
  // Function definition line.
  if (/^(?:function\s+)?[A-Za-z_][A-Za-z0-9_-]*\s*(?:\(\))?\s*\{/.test(trimmed)) return [];
  // Bare variable assignment with no command.
  if (/^[A-Za-z_][A-Za-z0-9_]*=/.test(trimmed) && !/[|&;<>()]|\$\(/.test(trimmed)) return [];

  const results = [];
  for (const segment of splitCommandSegments(trimmed)) {
    const command = segmentCommandName(segment);
    if (!command) continue;
    const operationType = classifyCommandName(command, segment);
    if (!operationType) continue;
    results.push({
      command,
      operationType,
      targets: extractCommandTargets(segment, operationType),
      segment
    });
  }
  return results;
}

/**
 * Map a command name (+ its segment for redirect/context signals) to an
 * operation_type, or '' if it carries no security-relevant action.
 * @param {string} command
 * @param {string} segment
 * @returns {string}
 */
function classifyCommandName(command, segment) {
  const name = String(command || '').toLowerCase();
  const base = name.split('/').pop();
  const text = String(segment || '').toLowerCase();

  if (EGRESS_COMMANDS.has(base)) return 'external_egress';
  // Redirection to a file makes any command a write.
  if (/>>?\s*[^&\s]/.test(text) || WRITE_COMMANDS.has(base) || /\btee\b/.test(text)) return 'write';
  if (EXEC_COMMANDS.has(base)) return 'invoke_tool';
  if (READ_COMMANDS.has(base)) return 'read';
  // echo/printf alone is just output; not a runtime action unless redirected
  // (handled above). Treat as no-op.
  if (/^(?:echo|printf|true|false|cd|export|set|unset|local|return|exit|shift|eval|source|\.)$/.test(base)) return '';
  // Unknown command with a URL argument → likely egress.
  if (URL_REGEX.test(text)) { URL_REGEX.lastIndex = 0; return 'external_egress'; }
  URL_REGEX.lastIndex = 0;
  return '';
}

function stripInlineComment(line) {
  const value = String(line || '');
  let inSingle = false;
  let inDouble = false;
  for (let i = 0; i < value.length; i++) {
    const ch = value[i];
    if (ch === "'" && !inDouble) inSingle = !inSingle;
    else if (ch === '"' && !inSingle) inDouble = !inDouble;
    else if (ch === '#' && !inSingle && !inDouble && (i === 0 || /\s/.test(value[i - 1]))) {
      return value.slice(0, i);
    }
  }
  return value;
}

const SHELL_FENCE_LANGS = new Set(['bash', 'sh', 'shell', 'console', 'zsh', 'ksh', 'shell-session', 'shellsession']);

/**
 * True when a fenced-code-block language marks it as shell/command content.
 * @param {string} lang
 * @returns {boolean}
 */
function isShellFenceLang(lang) {
  return SHELL_FENCE_LANGS.has(String(lang || '').trim().toLowerCase());
}

module.exports = {
  classifyShellCommandLine,
  classifyCommandName,
  splitCommandSegments,
  segmentCommandName,
  extractCommandTargets,
  isShellFenceLang,
  hostFromUrl
};
