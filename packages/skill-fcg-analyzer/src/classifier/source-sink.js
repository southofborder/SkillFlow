/**
 * Source/Sink Classifier
 * Classifies nodes as Source, Sink, or Intermediate based on naming patterns
 */

/**
 * Create implicit user query source node
 * In OpenClaw, the user's query is the initial data source that triggers Skill activation
 * @returns {Object} User query source node
 */
function createUserQuerySource() {
  return {
    name: 'user.query',
    action: 'query',
    type: 'builtin_call',
    description: 'User query that triggers Skill activation',
    input: {},
    output: {
      query_text: { type: 'string' },
      intent: { type: 'string' }
    },
    location: {
      file: 'OpenClaw Runtime',
      line: 0,
      section: 'Skill Activation Flow'
    }
  };
}

module.exports = {
  createUserQuerySource
};
