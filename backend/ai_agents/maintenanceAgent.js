const BaseAgent = require('./baseAgent');
const notificationService = require('../services/notificationService');

class MaintenanceAgent extends BaseAgent {
  constructor() {
    super();
    this.name = 'MaintenanceAgent';
    this.priority = 1;
    this.tools = [
      {
        name: 'report_issue',
        description: 'Report a maintenance issue in the room',
        parameters: {
          type: 'object',
          properties: {
            issue_type: {
              type: 'string',
              enum: ['plumbing', 'electrical', 'furniture', 'appliance', 'other'],
              description: 'Type of maintenance issue'
            },
            urgency: {
              type: 'string',
              enum: ['low', 'medium', 'high', 'emergency'],
              default: 'medium'
            },
            description: {
              type: 'string',
              description: 'Detailed description of the issue'
            }
          },
          required: ['issue_type']
        }
      },
      {
        name: 'schedule_maintenance',
        description: 'Schedule non-urgent maintenance',
        parameters: {
          type: 'object',
          properties: {
            issue_type: {
              type: 'string',
              enum: ['preventive', 'inspection', 'upgrade', 'cleaning'],
              description: 'Type of maintenance'
            },
            preferred_time: {
              type: 'string',
              description: 'Preferred time window for maintenance'
            }
          },
          required: ['issue_type']
        }
      }
    ];
  }

  shouldHandle(message) {
    const lowerMessage = message.toLowerCase();
    return this.tools.some(tool => 
      tool.name === 'report_issue' && (
        lowerMessage.includes('broken') ||
        lowerMessage.includes('repair') ||
        lowerMessage.includes('fix') ||
        lowerMessage.includes('not working')
      ) ||
      tool.name === 'schedule_maintenance' && (
        lowerMessage.includes('schedule') ||
        lowerMessage.includes('maintenance')
      )
    );
  }

  selectTool(message, history) {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('broken') || 
        lowerMessage.includes('repair') ||
        lowerMessage.includes('fix') ||
        lowerMessage.includes('not working')) {
      return this.tools.find(t => t.name === 'report_issue');
    }
    
    if (lowerMessage.includes('schedule') || 
        lowerMessage.includes('maintenance')) {
      return this.tools.find(t => t.name === 'schedule_maintenance');
    }
    
    return null;
  }

  async executeTool(tool, message, history) {
    const roomNumber = this.extractRoomNumber(history) || 'unknown';
    
    switch(tool.name) {
      case 'report_issue':
        return await this.handleIssueReport(roomNumber, message);
      case 'schedule_maintenance':
        return await this.handleMaintenanceSchedule(roomNumber, message);
      default:
        return {
          response: 'I couldn\'t process your maintenance request.',
          notifications: []
        };
    }
  }

  async handleIssueReport(roomNumber, message) {
    await notificationService.sendRoomNotification(
      roomNumber,
      `Maintenance issue reported: ${message}`
    );

    return {
      response: 'Your maintenance issue has been reported. A technician will be dispatched shortly.',
      notifications: [{
        type: 'maintenance',
        roomNumber,
        message: `Issue reported: ${message}`,
        urgency: this.determineUrgency(message)
      }]
    };
  }

  async handleMaintenanceSchedule(roomNumber, message) {
    await notificationService.sendRoomNotification(
      roomNumber,
      `Maintenance scheduled: ${message}`
    );

    return {
      response: 'Your maintenance has been scheduled. You will receive a confirmation shortly.',
      notifications: [{
        type: 'maintenance',
        roomNumber,
        message: `Scheduled: ${message}`,
        urgency: 'low'
      }]
    };
  }

  determineUrgency(message) {
    const lowerMessage = message.toLowerCase();
    if (lowerMessage.includes('emergency') || 
        lowerMessage.includes('urgent') ||
        lowerMessage.includes('flood') ||
        lowerMessage.includes('leak')) {
      return 'emergency';
    }
    if (lowerMessage.includes('important') ||
        lowerMessage.includes('asap')) {
      return 'high';
    }
    return 'medium';
  }

  extractRoomNumber(history) {
    for (const entry of history) {
      if (entry.role === 'user') {
        const roomMatch = entry.content.match(/room\s*(\d+)/i);
        if (roomMatch) return roomMatch[1];
      }
    }
    return null;
  }
}

module.exports = MaintenanceAgent;