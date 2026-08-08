const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');

/**
 * Parse SKILL.md file and extract front matter and content sections
 * @param {string} skillRootDir - Root directory of the skill
 * @returns {Object} Parsed skill data with front matter and content
 */
function parseSkill(skillRootDir) {
  const skillMdPath = path.join(skillRootDir, 'SKILL.md');
  
  if (!fs.existsSync(skillMdPath)) {
    throw new Error(`SKILL.md not found at: ${skillMdPath}`);
  }

  const content = fs.readFileSync(skillMdPath, 'utf-8');
  const parsed = matter(content);
  
  // Validate front matter
  if (!parsed.data.name || !parsed.data.description) {
    throw new Error('SKILL.md must have front matter with "name" and "description" fields');
  }

  // Extract sections from content
  const sections = extractSections(parsed.content);

  return {
    name: parsed.data.name,
    description: parsed.data.description,
    version: parsed.data.version || '1.0.0',
    content: parsed.content,
    sections,
    skillRootDir
  };
}

/**
 * Extract sections from markdown content
 * @param {string} content - Markdown content
 * @returns {Array} Array of sections with title, content, and line numbers
 */
function extractSections(content) {
  const lines = content.split('\n');
  const sections = [];
  let currentSection = null;
  let currentContent = [];
  let startLine = 1;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);
    
    if (headingMatch) {
      // Save previous section
      if (currentSection) {
        sections.push({
          ...currentSection,
          content: currentContent.join('\n'),
          endLine: i
        });
      }
      
      // Start new section
      currentSection = {
        title: headingMatch[2].trim(),
        level: headingMatch[1].length,
        startLine: i + 1
      };
      currentContent = [];
    } else if (currentSection) {
      currentContent.push(line);
    }
  }

  // Save last section
  if (currentSection) {
    sections.push({
      ...currentSection,
      content: currentContent.join('\n'),
      endLine: lines.length
    });
  }

  return sections;
}

/**
 * Parse README.md if it exists
 * @param {string} skillRootDir - Root directory of the skill
 * @returns {Object|null} Parsed README data or null
 */
function parseReadme(skillRootDir) {
  const readmePath = path.join(skillRootDir, 'README.md');
  
  if (!fs.existsSync(readmePath)) {
    return null;
  }

  const content = fs.readFileSync(readmePath, 'utf-8');
  return {
    content,
    exists: true
  };
}

const EXECUTABLE_EXTENSIONS = new Set(['.js', '.mjs', '.cjs', '.ts', '.tsx', '.sh', '.bash']);

/**
 * Find executable source files in the skill directory.
 * @param {string} skillRootDir - Root directory of the skill
 * @returns {Array} Array of executable file paths
 */
function findExecutableFiles(skillRootDir) {
  const executableFiles = [];
  const ignoredDirs = new Set([
    'node_modules',
    '.git',
    '.svn',
    '.hg',
    'dist',
    'build',
    'coverage'
  ]);
  
  function walkDir(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      
      if (entry.isDirectory()) {
        if (ignoredDirs.has(entry.name)) {
          continue;
        }
        walkDir(fullPath);
      } else if (isExecutableSourceFile(fullPath)) {
        executableFiles.push(fullPath);
      }
    }
  }
  
  walkDir(skillRootDir);
  return executableFiles;
}

function isExecutableSourceFile(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (EXECUTABLE_EXTENSIONS.has(ext)) return true;
  try {
    const firstLine = fs.readFileSync(filePath, 'utf-8').split(/\r?\n/, 1)[0] || '';
    return /^#!.*\b(?:node|bash|sh)\b/.test(firstLine);
  } catch (_) {
    return false;
  }
}

module.exports = {
  parseSkill,
  parseReadme,
  findExecutableFiles,
  extractSections
};
