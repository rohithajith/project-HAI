const BaseAgent = require('./baseAgent');
const notificationService = require('../services/notificationService');

class RoomServiceAgent extends BaseAgent {
  constructor() {
    super();
    this.name = 'RoomServiceAgent';
    this.priority = 1;
    this.tools = [
      {
        name: 'order_food',
        description: 'Place food order from room service menu',
        parameters: {
          type: 'object',
          properties: {
            items: {
              type: 'array',
              items: { type: 'string' },
              description: 'List of food items to order'
            },
            special_instructions: {
              type: 'string',
              description: 'Any special preparation instructions'
            }
          },
          required: ['items']
        }
      },
      {
        name: 'order_drinks',
        description: 'Place drink order from room service menu',
        parameters: {
          type: 'object',
          properties: {
            beverages: {
              type: 'array',
              items: { type: 'string' },
              description: 'List of beverages to order'
            },
            ice_preference: {
              type: 'string',
              enum: ['none', 'light', 'regular', 'extra'],
              description: 'Ice preference for drinks'
            }
          },
          required: ['beverages']
        }
      }
    ];
  }

  shouldHandle(message) {
    const lowerMessage = message.toLowerCase();
    return lowerMessage.includes('room service') || 
           lowerMessage.includes('food') ||
           lowerMessage.includes('drink') ||
           lowerMessage.includes('menu') ||
           lowerMessage.includes('order');
  }

  selectTool(message, history) {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('food') || lowerMessage.includes('menu')) {
      return this.tools.find(t => t.name === 'order_food');
    }
    
    if (lowerMessage.includes('drink') || lowerMessage.includes('beverage')) {
      return this.tools.find(t => t.name === 'order_drinks');
    }
    
    return null;
  }

  async executeTool(tool, message, history) {
    const roomNumber = this.extractRoomNumber(history) || 'unknown';
    
    switch(tool.name) {
      case 'order_food':
        return await this.handleFoodOrder(roomNumber, message);
      case 'order_drinks':
        return await this.handleDrinkOrder(roomNumber, message);
      default:
        return {
          response: 'I couldn\'t process your room service request.',
          notifications: []
        };
    }
  }

  async handleFoodOrder(roomNumber, message) {
    await notificationService.sendRoomNotification(
      roomNumber,
      `Food order placed: ${message}`
    );

    return {
      response: 'Your food order has been placed. It will arrive in approximately 30 minutes.',
      notifications: [{
        type: 'room_service',
        roomNumber,
        message: `Food order: ${message}`
      }]
    };
  }

  async handleDrinkOrder(roomNumber, message) {
    await notificationService.sendRoomNotification(
      roomNumber,
      `Drink order placed: ${message}`
    );

    return {
      response: 'Your drink order has been placed. It will arrive in approximately 15 minutes.',
      notifications: [{
        type: 'room_service',
        roomNumber,
        message: `Drink order: ${message}`
      }]
    };
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

module.exports = RoomServiceAgent;