/**
 * Basic logger service
 * Provides console-based logging for development
 */

const logger = {
  info: (message) => {
    console.log(`[INFO] ${message}`);
  },
  error: (message) => {
    console.error(`[ERROR] ${message}`);
  },
  warn: (message) => {
    console.warn(`[WARN] ${message}`);
  }
};

module.exports = logger;