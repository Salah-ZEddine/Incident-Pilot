import type { Alert } from '../types/Alert.js';
import { IDatabaseService } from './Idatabase.js';
import { Pool } from 'pg';
import { POSTGRES_CONNECTION_STRING } from '../config/postgres.config.js';

export class PostgresDatabaseService implements IDatabaseService {
  private pool: Pool;

  constructor() {
    this.pool = new Pool({
      connectionString: POSTGRES_CONNECTION_STRING,
    });
  }

  async init(): Promise<void> {
    // Initialize database connection
    await this.pool.connect();
  }

  async close(): Promise<void> {
    // Close database connection
    await this.pool.end();
  }

  async insertAlert(alert: Alert): Promise<Alert> {
    // Insert alert into PostgreSQL database
    const query = `
      INSERT INTO alerts (alert_id, timestamp, rule_name, description, severity, log_reference_ids, tags, detected_by, suggested_action, facts)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
      RETURNING alert_id;
    `;
    const values = [
      alert.timestamp,
      alert.rule_name,
      alert.description,
      alert.severity,
      alert.log_reference_ids,
      alert.tags,
      alert.detected_by,
      alert.suggested_action,
      alert.facts,
    ];
    const result = await this.pool.query(query, values);
    return result.rows[0];
  }
}