const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false } // Required for external Postgres providers like Neon
});

module.exports = {
    query: (text, params) => pool.query(text, params),
    pool
};
