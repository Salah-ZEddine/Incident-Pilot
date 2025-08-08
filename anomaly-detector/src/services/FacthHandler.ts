import { Fact } from '../types/Fact.js';
import { Alert } from '../types/Alert.js';
import { IDatabaseService } from '../db/Idatabase.js';
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
    private database: IDatabaseService;

    constructor(rules: Rule[] = [], database: IDatabaseService) {
        this.engine = new Engine(rules);
        this.logger = console;
        this.database = database;

        this.logger.log(`🔧 FactHandler initialized with ${rules.length} rules`);
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
                this.logger.log(`✅ No anomalies detected for ${fact.source} (${processingTime}ms)`);
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

        this.logger.log(`🚨 ${anomalies.length} anomalies detected for ${fact.source} (${processingTimeMs}ms):`,
            anomalies.map(event => ({
                type: event.type,
                params: event.params
            }))
        );

        // Process each anomaly and create corresponding alerts
        for (const anomaly of anomalies) {
            try {
                // Convert anomaly to alert schema
                let alert: Alert = this.createAlertFromAnomaly(fact, anomaly);
                
                // Save alert to database using the insertAlert method
                alert = await this.database.insertAlert(alert);
                
                this.logger.log(`✅ Alert created and saved: ${alert.alert_id} for anomaly ${anomaly.type} from ${fact.source}`);
                
                // Continue with other anomaly processing (Kafka, etc.)
                await this.processAnomaly(fact, anomaly);
                
            } catch (error) {
                this.logger.error(`❌ Failed to create/save alert for anomaly ${anomaly.type}:`, {
                    error: error instanceof Error ? error.message : String(error),
                    fact: this.sanitizeFactForLogging(fact),
                    anomaly: {
                        type: anomaly.type,
                        params: anomaly.params
                    }
                });
            }
        }
    }


    private createAlertFromAnomaly(fact: Fact, anomaly: Event): Alert {        
        // Determine severity based on anomaly type and parameters
        const severity = this.determineSeverity(anomaly);
        
        // Generate rule name from anomaly type
        const ruleName = this.generateRuleName(anomaly.type);
        
        // Create descriptive alert description
        const description = this.generateAlertDescription(fact, anomaly);
        
        // Generate tags for categorization
        const tags = this.generateAlertTags(fact, anomaly);
        
        // Suggest action based on anomaly type
        const suggestedAction = this.generateSuggestedAction(anomaly);
        
        // Create log reference IDs (if your fact has log IDs)
        const logReferenceIds = this.extractLogReferenceIds(fact);

        const alert: Alert = {
            timestamp: new Date(),
            rule_name: ruleName,
            description,
            severity,
            log_reference_ids: logReferenceIds,
            tags,
            detected_by: 'anomaly-detector-service',
            suggested_action: suggestedAction,
            facts: {
                // Include all relevant fact data
                source: fact.source,
                timestamp: fact.timestamp,
                anomaly_type: anomaly.type,
                anomaly_params: anomaly.params,
                error_count: fact.repeated_error_count,
                // warning_count: fact.warning_count,
                // failed_syscalls: fact.failed_syscalls,
                potential_scraper: fact.potential_scraper,
                is_silent: fact.is_silent,
                // Include fact data that might be relevant for investigation
                // ...(fact.source_ip && { source_ip: fact.source_ip }),
                // ...(fact.destination_ip && { destination_ip: fact.destination_ip }),
                // ...(fact.user_id && { user_id: fact.user_id }),
                // ...(fact.username && { username: fact.username }),
                // ...(fact.http_method && { http_method: fact.http_method }),
                // ...(fact.http_url && { http_url: fact.http_url }),
                // ...(fact.http_status && { http_status: fact.http_status }),
                // ...(fact.user_agent && { user_agent: fact.user_agent })
            }
        };

        return alert;
    }


    private determineSeverity(anomaly: Event): 'low' | 'medium' | 'high' | 'critical' {
        const params = anomaly.params || {};
        
        // Define severity mapping based on anomaly types
        const severityMap: Record<string, 'low' | 'medium' | 'high' | 'critical'> = {
            'high-error-rate': 'high',
            'potential-attack': 'critical',
            'suspicious-activity': 'high',
            'unauthorized-access': 'critical',
            'security-violation': 'critical',
            'potential-scraper': 'medium',
            'failed-syscalls': 'high',
            'silence-detected': 'medium',
            'repeated-errors': 'medium',
            'performance-degradation': 'medium',
            'system-anomaly': 'medium'
        };

        // Override severity based on specific parameters
        if (params.count && typeof params.count === 'number') {
            if (params.count > 100) return 'critical';
            if (params.count > 50) return 'high';
        }
        
        if (params.rate && typeof params.rate === 'number') {
            if (params.rate > 0.9) return 'critical';
            if (params.rate > 0.7) return 'high';
        }

        if (params.security_level === 'critical') return 'critical';

        return severityMap[anomaly.type] || 'medium';
    }

    private generateRuleName(anomalyType: string): string {
        // Convert anomaly type to readable rule name
        const ruleNameMap: Record<string, string> = {
            'high-error-rate': 'High Error Rate Detection',
            'potential-attack': 'Potential Attack Pattern',
            'suspicious-activity': 'Suspicious Activity Detection',
            'unauthorized-access': 'Unauthorized Access Attempt',
            'security-violation': 'Security Policy Violation',
            'potential-scraper': 'Potential Web Scraper',
            'failed-syscalls': 'System Call Failure',
            'silence-detected': 'Service Silence Detection',
            'repeated-errors': 'Repeated Error Pattern',
            'performance-degradation': 'Performance Degradation',
            'system-anomaly': 'System Anomaly Detection'
        };

        return ruleNameMap[anomalyType] || `Unknown Anomaly: ${anomalyType}`;
    }

    private generateAlertDescription(fact: Fact, anomaly: Event): string {
        const params = anomaly.params || {};
        
        switch (anomaly.type) {
            case 'high-error-rate':
                return `High error rate detected from ${fact.source}: ${params.count || 'N/A'} errors in ${params.timeWindow || 'unknown'} timeframe (${params.rate || 'N/A'}% error rate)`;
                
            case 'potential-scraper':
                return `Potential web scraping detected from ${fact.source}: ${params.requestCount || 'N/A'} requests to ${params.uniqueUrls || 'N/A'} unique URLs in rapid succession`;
                
            case 'suspicious-activity':
                return `Suspicious activity pattern detected from ${fact.source}: ${params.pattern || 'Unknown pattern'}. ${params.description || 'No additional details'}`;
                
            case 'unauthorized-access':
                return `Unauthorized access attempts detected: ${params.attempts || 'N/A'} failed authentication attempts for ${ 'unknown user'} from ${ fact.source}`;
                
            case 'failed-syscalls':
                return `System call failures detected from ${fact.source}: ${params.failureType || 'Unknown type'} failures in critical system operations`;
                
            case 'silence-detected':
                return `Service silence detected: No activity from ${fact.source} for ${params.silenceDuration || 'extended'} period, indicating potential service failure`;
                
            case 'repeated-errors':
                return `Repeated error pattern from ${fact.source}: Same error message occurred ${params.count || 'multiple'} times, indicating systemic issue`;
                
            default:
                return `Anomaly detected from ${fact.source}: ${anomaly.type}. Parameters: ${JSON.stringify(params)}`;
        }
    }

    private generateAlertTags(fact: Fact, anomaly: Event): string[] {
        const tags = ['anomaly-detection'];
        
        // Add tags based on anomaly type
        switch (anomaly.type) {
            case 'potential-attack':
            case 'unauthorized-access':
            case 'security-violation':
                tags.push('security', 'threat');
                break;
            case 'potential-scraper':
                tags.push('security', 'automation', 'scraping');
                break;
            case 'high-error-rate':
            case 'repeated-errors':
                tags.push('performance', 'errors');
                break;
            case 'failed-syscalls':
                tags.push('system', 'infrastructure');
                break;
            case 'silence-detected':
                tags.push('availability', 'monitoring');
                break;
        }
        
        // Add source-based tags
        if (fact.source) {
            tags.push(`source:${fact.source}`);
        }
        
        // Add severity tag
        const severity = this.determineSeverity(anomaly);
        tags.push(`severity:${severity}`);
        
        return tags;
    }

    private generateSuggestedAction(anomaly: Event): string {
        const actionMap: Record<string, string> = {
            'high-error-rate': 'Investigate error logs, check system resources, review recent deployments',
            'potential-attack': 'Block suspicious IPs, review security logs, activate incident response',
            'suspicious-activity': 'Monitor closely, review user behavior, consider security assessment',
            'unauthorized-access': 'Block source IP, review authentication logs, reset affected credentials',
            'security-violation': 'Immediate security review, check access controls, audit user permissions',
            'potential-scraper': 'Implement rate limiting, consider IP blocking, review bot protection',
            'failed-syscalls': 'Check system health, review resource availability, investigate infrastructure',
            'silence-detected': 'Check service health, verify connectivity, investigate potential outage',
            'repeated-errors': 'Review application logs, check configuration, investigate root cause'
        };

        return actionMap[anomaly.type] || 'Review anomaly details and investigate further';
    }

    private extractLogReferenceIds(fact: Fact): string[] {
        // Extract log reference IDs if available in your fact structure
        const logIds: string[] = [];
        
        // If your fact has a log ID field
        if ('log_id' in fact && fact.log_id) {
            logIds.push(String(fact.log_id));
        }
        
        // If your fact has related log IDs
        if ('related_log_ids' in fact && Array.isArray(fact.related_log_ids)) {
            logIds.push(...fact.related_log_ids.map(id => String(id)));
        }
        
        // If no specific log IDs, create a reference based on fact timestamp and source
        if (logIds.length === 0) {
            const reference = `${fact.source}-${fact.timestamp?.toString() || new Date().toISOString()}`;
            logIds.push(reference);
        }
        
        return logIds;
    }

    private async processAnomaly(fact: Fact, anomaly: Event): Promise<void> {
        // Placeholder for specific anomaly processing
        // This is where you'd emit to Kafka, send alerts, etc.
        this.logger.log(`📤 Processing anomaly: ${anomaly.type} for ${fact.source}`);
        
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
        
        // const { message, ...safeFact } = fact;
        // return {
        //     ...safeFact,
        //     message: message ? `${message.substring(0, 100)}...` : undefined
        // };
    }

    public addRule(rule: Rule): void {
        this.engine.addRule(rule);
        this.logger.log(`Added rule: ${rule.name || 'unnamed'}`);
    }

    public clearRules(): void {
        this.engine = new Engine();
        this.logger.log(`All rules cleared`);
    }

}