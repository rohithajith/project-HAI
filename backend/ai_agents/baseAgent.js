class BaseAgent {
  constructor() {
    this.name = 'BaseAgent';
    this.priority = 0;
    this.tools = [];
  }

  /**
   * Check if this agent should handle the message
   * @param {string} message - User message
   * @param {Array} history - Conversation history
   * @returns {boolean} True if agent should handle this message
   */
  shouldHandle(message, history) {
    return false;
  }

  /**
   * Get available tools for this agent
   * @returns {Array} List of tool definitions
   */
  getAvailableTools() {
    return this.tools;
  }

  /**
   * Select appropriate tool for the message
   * @param {string} message - User message
   * @param {Array} history - Conversation history
   * @returns {Object|null} Selected tool or null
   */
  selectTool(message, history) {
    return null;
  }

  /**
   * Execute tool and return results
   * @param {Object} tool - Tool to execute
   * @param {string} message - User message
   * @param {Array} history - Conversation history
   * @returns {Promise<Object>} Tool execution results
   */
  async executeTool(tool, message, history) {
    return {
      response: '',
      notifications: []
    };
  }

  /**
   * Process the message and return response and notifications
   * @param {string} message - User message
   * @param {Array} history - Conversation history
   * @returns {Promise<{response: string, notifications: Array, toolUsed: boolean}>}
   */
  async process(message, history) {
    const tool = this.selectTool(message, history);
    if (tool) {
      const result = await this.executeTool(tool, message, history);
      return {
        ...result,
        toolUsed: true
      };
    }

    return {
      response: '',
      notifications: [],
      toolUsed: false
    };
  }
}

module.exports = BaseAgent;