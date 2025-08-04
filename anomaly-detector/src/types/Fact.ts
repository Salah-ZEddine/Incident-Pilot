export interface Fact {
  timestamp: string;            // ISO8601 datetime string (serialize datetime to ISO)
  source: string;
  log_level: string;
  message: string;

  repeated_error_count?: number;     // default 0
  recent_error_count?: number;       // default 0
  recent_warn_count?: number;        // default 0
  log_frequency_last_minute?: number; // default 0

  is_silent?: boolean;               // default false
  matched_pattern?: string | null;  // can be null or string
  failed_syscall?: boolean;          // default false
  unauthorized_count?: number;       // default 0
  potential_scraper?: boolean;       // default false

  performance_latency?: number | null; // float or null
}
