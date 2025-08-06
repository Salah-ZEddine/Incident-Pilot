export type Alert = {
  alert_id: string;
  timestamp: Date; 
  rule_name: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  log_reference_ids: string[];
  tags: string[];
  detected_by: string;
  suggested_action: string;
  facts: Record<string, any>; // or a more strict type if needed
};
