import { Fact } from '../types/Fact.ts;

export class FactHandler {
    
    private ruleEngine: any;

    constructor(ruleEngine: any) {
        this.ruleEngine = ruleEngine;
    }

    public async handleFact(fact: Fact): Promise<void> {
         try {
        // Apply rules to the fact
        const results = await this.ruleEngine.evaluate(fact);

        // Optionally: handle the results (e.g., log, alert, store)
        if (results.length > 0) {
            console.log(" Anomalies detected:", results);
            // emit to kafka or whatever 
        } else {
            console.log("No anomalies detected.");
        }
        } catch (error) {
        console.error(" Error handling fact:", error);
        }
    }
}