import dotenv from 'dotenv';

dotenv.config();

const {
  POSTGRES_USER,
  POSTGRES_PASSWORD,
  POSTGRES_DB,
  POSTGRES_HOST,
  POSTGRES_PORT,
} = process.env;

if (!POSTGRES_USER || !POSTGRES_PASSWORD || !POSTGRES_DB || !POSTGRES_HOST || !POSTGRES_PORT) {
  throw new Error('Missing required PostgreSQL environment variables.');
}

export const POSTGRES_CONNECTION_STRING = `postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}`;
