import { Fact } from '../types/Fact.js';
import { Engine, Rule, Event } from 'json-rules-engine';

export interface AnomalyResult {
    fact: Fact;
    anomalies: Event[];
    processedAt: Date;
    processingTimeMs: number;
}

export class FactHandler {
    
    private engine: Engine;
    private readonly logger: Console;

    constructor(rules: Rule[] = []) {
        this.engine = new Engine(rules); // Rules are added via constructor
        this.logger = console; // Could be replaced with proper logger
        
        console.log(`🔧 FactHandler initialized with ${rules.length} rules`);
    }

    public async handleFact(fact: Fact): Promise<AnomalyResult> {
        const startTime = Date.now();
        
        try {
            // Validate fact structure
            if (!fact || typeof fact !== 'object') {
                throw new Error('Invalid fact provided');
            }

            console.log(`🔍 Processing fact from source: ${fact.source}`);
            
            // Apply rules to the fact
            const results = await this.engine.run(fact);
            const processingTime = Date.now() - startTime;

            // Create structured result
            const anomalyResult: AnomalyResult = {
                fact,
                anomalies: results.events,
                processedAt: new Date(),
                processingTimeMs: processingTime
            };

            // Handle results based on findings
            if (results.events.length > 0) {
                await this.handleAnomalies(anomalyResult);
            } else {
                console.log(`✅ No anomalies detected for ${fact.source} (${processingTime}ms)`);
            }

            return anomalyResult;

        } catch (error) {
            const processingTime = Date.now() - startTime;
            console.error(`❌ Error processing fact from ${fact?.source || 'unknown'}:`, {
                error: error instanceof Error ? error.message : String(error),
                fact: this.sanitizeFactForLogging(fact),
                processingTimeMs: processingTime
            });
            
            // Return error result
            return {
                fact,
                anomalies: [],
                processedAt: new Date(),
                processingTimeMs: processingTime
            };
        }
    }

    private async handleAnomalies(result: AnomalyResult): Promise<void> {
        const { fact, anomalies, processingTimeMs } = result;
        
        console.log(`🚨 ${anomalies.length} anomalies detected for ${fact.source} (${processingTimeMs}ms):`, 
            anomalies.map(event => ({
                type: event.type,
                params: event.params
            }))
        );

        // TODO: Implement actual anomaly handling
        // - Send to Kafka
        // - Store in database
        // - Trigger alerts
        // - Update metrics
        
        for (const anomaly of anomalies) {
            await this.processAnomaly(fact, anomaly);
        }
    }

    private async processAnomaly(fact: Fact, anomaly: Event): Promise<void> {
        // Placeholder for specific anomaly processing
        // This is where you'd emit to Kafka, send alerts, etc.
        console.log(`📤 Processing anomaly: ${anomaly.type} for ${fact.source}`);
        
        // Example: Emit to Kafka
        // await this.kafkaProducer.send({
        //     topic: 'anomalies',
        //     messages: [{
        //         key: fact.source,
        //         value: JSON.stringify({ fact, anomaly, timestamp: new Date() })
        //     }]
        // });
    }

    private sanitizeFactForLogging(fact: Fact): any {
        // Remove sensitive data for logging
        if (!fact) return {};
        
        const { message, ...safeFact } = fact;
        return {
            ...safeFact,
            message: message ? `${message.substring(0, 100)}...` : undefined
        };
    }

    public addRule(rule: Rule): void {
        this.engine.addRule(rule);
        console.log(`Added rule: ${rule.name || 'unnamed'}`);
    }

    public clearRules(): void {
        this.engine = new Engine();
        console.log(`All rules cleared`);
    }

}