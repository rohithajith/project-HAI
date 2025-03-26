const RoomServiceAgent = require('./roomServiceAgent');
const MaintenanceAgent = require('./maintenanceAgent');

class AgentManager {
  constructor() {
    this.agents = [
      new RoomServiceAgent(),
      new MaintenanceAgent()
    ].sort((a, b) => b.priority - a.priority); // Higher priority first
  }

  /**
   * Process message through agents with tool support
   * @param {string} message 
   * @param {Array} history 
   * @returns {Promise<{response: string, notifications: Array, toolUsed: boolean}>}
   */
  async process(message, history) {
    // Try each agent in priority order
    for (const agent of this.agents) {
      if (agent.shouldHandle(message, history)) {
        const result = await agent.process(message, history);
        
        // If agent used a tool, return its result
        if (result.toolUsed) {
          return {
            response: result.response,
            notifications: result.notifications || [],
            toolUsed: true
          };
        }
        
        // If agent handled it but didn't use a tool
        if (result.response) {
          return {
            response: result.response,
            notifications: result.notifications || [],
            toolUsed: false
          };
        }
      }
    }

    // If no agent handled it, return empty result to fall through to model
    return {
      response: '',
      notifications: [],
      toolUsed: false
    };
  }

  /**
   * Get all available tools from all agents
   * @returns {Array} Combined list of all tools
   */
  getAllTools() {
    return this.agents.flatMap(agent => agent.getAvailableTools());
  }
}

module.exports = AgentManager;