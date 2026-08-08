// Parity driver for front-matter: read a JSON array of raw SKILL.md strings from
// argv[2], run real gray-matter on each, print [{data, content}] to stdout.
// Paired with test_parity_frontmatter.py to lock body-split + YAML parse.
const fs = require('fs');
const matter = require('../../../skill-fcg-analyzer/node_modules/gray-matter');

const inputs = JSON.parse(fs.readFileSync(process.argv[2], 'utf-8'));
const out = inputs.map(raw => {
  const parsed = matter(raw);
  return { data: parsed.data, content: parsed.content };
});
process.stdout.write(JSON.stringify(out));
