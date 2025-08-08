import { KafkaService } from './services/KafkaService.js';
import { FactHandler } from './services/FacthHandler.js';
import { PostgresDatabaseService } from './db/postgres.databse.js';
import { Fact } from './types/Fact.js';
import { EachMessagePayload } from 'kafkajs';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class AnomalyDetectorService {
  private factHandler: FactHandler;
  private kafkaService: KafkaService;
  private database: PostgresDatabaseService;

  constructor() {
    this.database = new PostgresDatabaseService();
    this.factHandler = new FactHandler([], this.database);
    this.kafkaService = new KafkaService(
      process.env.KAFKA_FACT_TOPIC || 'logs_fact',
      this.handleMessage.bind(this)
    );
  }

  async start(): Promise<void> {
    try {
      console.log('🚀 Starting Anomaly Detector Service...');
      
      // Initialize database
      await this.database.init();
      
      // Load rules
      await this.loadRules();
      
      // Start Kafka consumer
      await this.kafkaService.start();
      
      console.log('✅ Anomaly Detector Service started successfully!');
      console.log('📥 Listening for facts on Kafka topic...');
      
    } catch (error) {
      console.error('❌ Failed to start Anomaly Detector Service:', error);
      process.exit(1);
    }
  }

  async stop(): Promise<void> {
    console.log('🛑 Stopping Anomaly Detector Service...');
    
    try {
      await this.kafkaService.stop();
      await this.database.close();
      console.log('✅ Anomaly Detector Service stopped successfully!');
    } catch (error) {
      console.error('❌ Error stopping service:', error);
    }
  }

  private async loadRules(): Promise<void> {
    try {
      const rulesDir = path.join(__dirname, '../rules');
      
      if (!fs.existsSync(rulesDir)) {
        console.warn('⚠️ Rules directory not found, creating with sample rules...');
        // this.createSampleRules(rulesDir);
      }

      const ruleFiles = fs.readdirSync(rulesDir).filter(file => file.endsWith('.json'));
      
      console.log(`📋 Loading ${ruleFiles.length} rules...`);
      
      for (const file of ruleFiles) {
        const rulePath = path.join(rulesDir, file);
        const ruleContent = fs.readFileSync(rulePath, 'utf8');
        const rule = JSON.parse(ruleContent);
        
        // Add rule name from filename if not present
        if (!rule.name) {
          rule.name = path.basename(file, '.json');
        }
        
        this.factHandler.addRule(rule);
      }
      
      console.log(`✅ Loaded ${ruleFiles.length} rules successfully`);
      
    } catch (error) {
      console.error('❌ Error loading rules:', error);
      throw error;
    }
  }

//   private createSampleRules(rulesDir: string): void {
//     fs.mkdirSync(rulesDir, { recursive: true });
    
//     const sampleRules = [
//       {
//         name: 'high-error-rate',
//         conditions: {
//           all: [
//             { fact: 'repeated_error_count', operator: 'greaterThan', value: 10 }
//           ]
//         },
//         event: {
//           type: 'high-error-rate',
//           params: { severity: 'high', description: 'High error rate detected' }
//         }
//       },
//       {
//         name: 'potential-scraper',
//         conditions: {
//           all: [
//             { fact: 'potential_scraper', operator: 'equal', value: true }
//           ]
//         },
//         event: {
//           type: 'potential-scraper',
//           params: { severity: 'medium', description: 'Potential web scraper detected' }
//         }
//       },
//       {
//         name: 'silence-detection',
//         conditions: {
//           all: [
//             { fact: 'is_silent', operator: 'equal', value: true }
//           ]
//         },
//         event: {
//           type: 'silence-detected',
//           params: { severity: 'medium', description: 'Service silence detected' }
//         }
//       },
//       {
//         name: 'repeated-errors',
//         conditions: {
//           all: [
//             { fact: 'repeated_error_count', operator: 'greaterThan', value: 5 }
//           ]
//         },
//         event: {
//           type: 'repeated-errors',
//           params: { severity: 'medium', description: 'Repeated errors detected' }
//         }
//       }
//     ];

//     sampleRules.forEach(rule => {
//       fs.writeFileSync(
//         path.join(rulesDir, `${rule.name}.json`),
//         JSON.stringify(rule, null, 2)
//       );
//     });

//     console.log(`📋 Created ${sampleRules.length} sample rules`);
//   }

  private async handleMessage(payload: EachMessagePayload): Promise<void> {
    try {
      const messageValue = payload.message.value?.toString();
      if (!messageValue) {
        console.warn('⚠️ Received empty message');
        return;
      }

      const fact: Fact = JSON.parse(messageValue);
      
      console.log(`📥 Processing fact from ${fact.source}`);
      
      // Process the fact through the anomaly detection engine
      const result = await this.factHandler.handleFact(fact);
      
      if (result.anomalies.length > 0) {
        console.log(`🚨 Detected ${result.anomalies.length} anomalies for ${fact.source}`);
      }
      
    } catch (error) {
      console.error('❌ Error processing message:', error);
      console.error('Message payload:', payload.message.value?.toString());
    }
  }
}

// Main execution
async function main() {
  const service = new AnomalyDetectorService();

  // Graceful shutdown handling
  process.on('SIGINT', async () => {
    console.log('\n🛑 Received SIGINT, shutting down gracefully...');
    await service.stop();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    console.log('\n🛑 Received SIGTERM, shutting down gracefully...');
    await service.stop();
    process.exit(0);
  });

  process.on('uncaughtException', async (error) => {
    console.error('💥 Uncaught Exception:', error);
    await service.stop();
    process.exit(1);
  });

  process.on('unhandledRejection', async (reason, promise) => {
    console.error('💥 Unhandled Rejection at:', promise, 'reason:', reason);
    await service.stop();
    process.exit(1);
  });

  // Start the service
  try {
    await service.start();
  } catch (error) {
    console.error('💥 Fatal error during startup:', error);
    process.exit(1);
  }
}

// Execute main function
main().catch(error => {
  console.error('💥 Fatal error in main:', error);
  process.exit(1);
});