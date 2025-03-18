const { Pool } = require('pg');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// PostgreSQL connection configuration
const pool = new Pool({
  user: process.env.PGUSER || 'postgres',
  host: process.env.PGHOST || 'localhost',
  database: process.env.PGDATABASE || 'hotel_management',
  password: process.env.PGPASSWORD || 'postgres',
  port: process.env.PGPORT || 5432,
});

// Test the connection
pool.connect((err, client, release) => {
  if (err) {
    console.error('Database connection error:', err.message);
    return;
  }
  console.log('Connected to PostgreSQL database');
  release();
});

// Helper functions to wrap PostgreSQL queries in promises
const dbAsync = {
  /**
   * Execute a query with parameters and return all rows
   * @param {string} text - SQL query text
   * @param {Array} params - Query parameters
   * @returns {Promise<Array>} - Promise resolving to array of rows
   */
  query: async (text, params = []) => {
    try {
      const result = await pool.query(text, params);
      return result.rows;
    } catch (err) {
      console.error('Database query error:', err);
      throw err;
    }
  },

  /**
   * Execute a query with parameters and return a single row
   * @param {string} text - SQL query text
   * @param {Array} params - Query parameters
   * @returns {Promise<Object>} - Promise resolving to a single row
   */
  queryOne: async (text, params = []) => {
    try {
      const result = await pool.query(text, params);
      return result.rows[0];
    } catch (err) {
      console.error('Database query error:', err);
      throw err;
    }
  },

  /**
   * Execute a query that modifies data and return result
   * @param {string} text - SQL query text
   * @param {Array} params - Query parameters
   * @returns {Promise<Object>} - Promise resolving to query result
   */
  execute: async (text, params = []) => {
    try {
      const result = await pool.query(text, params);
      return {
        rowCount: result.rowCount,
        rows: result.rows
      };
    } catch (err) {
      console.error('Database execute error:', err);
      throw err;
    }
  },

  /**
   * Execute a query that inserts data and return the inserted ID
   * @param {string} text - SQL query text with RETURNING id
   * @param {Array} params - Query parameters
   * @returns {Promise<number>} - Promise resolving to inserted ID
   */
  insert: async (text, params = []) => {
    try {
      // Ensure the query includes RETURNING id
      if (!text.toLowerCase().includes('returning')) {
        text += ' RETURNING id';
      }
      const result = await pool.query(text, params);
      return result.rows[0]?.id;
    } catch (err) {
      console.error('Database insert error:', err);
      throw err;
    }
  },

  /**
   * Execute a transaction with multiple queries
   * @param {Function} callback - Async function that receives a client to execute queries
   * @returns {Promise<any>} - Promise resolving to the result of the callback
   */
  transaction: async (callback) => {
    const client = await pool.connect();
    try {
      await client.query('BEGIN');
      const result = await callback(client);
      await client.query('COMMIT');
      return result;
    } catch (err) {
      await client.query('ROLLBACK');
      console.error('Transaction error:', err);
      throw err;
    } finally {
      client.release();
    }
  }
};

module.exports = dbAsync;