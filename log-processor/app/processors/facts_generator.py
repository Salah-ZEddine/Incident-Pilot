from app.config import Settings
from app.models.log_model import LogModel
from app.models.fact_model import Fact
from app.processors.cache import get_logs_within, push_log_history, get_last_seen, set_last_seen
from datetime import datetime, timedelta
import re

SUSPICIOUS_PATTERNS = [
    r"unauthorized", r"login failed", r"403", r"panic:", r"segfault",
    r"sql injection", r"out of memory", r"oom", r"failed to connect",
    r"timeout", r"connection refused", r"disk full"
]


class FactGenerator:
    def __init__(self, log: LogModel):
        self.log = log

    def generate_facts_from_log(self) -> Fact:
        # Ensure we have a valid source
        source = self.log.source or 'unknown'
        
        # Push current log to history (use mode='json' for proper datetime serialization)
        push_log_history(source, self.log.model_dump(mode='json'))
        set_last_seen(source, self.log.timestamp)

        # Get logs in past 2min/5min/1min
        last_2min = get_logs_within(source, 120) or []
        last_5min = get_logs_within(source, 300) or []
        last_1min = get_logs_within(source, 60) or []

        # Count occurrences
        error_logs = [l for l in last_2min if l.get("log_level") == "ERROR"]
        warn_logs = [l for l in last_5min if l.get("log_level") == "WARN"]
        repeated_errors = [
            l for l in last_2min if l.get("log_level") == "ERROR" and l.get("message") == self.log.message
        ]
        unauthorized_logs = [
            l for l in last_5min if any(k in (l.get("message") or "").lower() for k in ["unauthorized", "login failed", "403"])
        ]
        failed_syscalls = bool(
            re.search(r"(failed to connect|timeout|connection refused|disk full)", self.log.message or "", re.IGNORECASE)
        )

        matched_pattern = next((p for p in SUSPICIOUS_PATTERNS if re.search(p, self.log.message or "", re.IGNORECASE)), None)

        # Silence detection
        last_seen = get_last_seen(source)
        is_silent = False
        if last_seen:
            silence_threshold = self.log.timestamp - timedelta(minutes=10)
            is_silent = last_seen < silence_threshold

        # Potential scrapers: too many GETs to different URLs
        get_requests = [l for l in last_1min if l.get("http_method") == "GET"]
        distinct_urls = set([l.get("http_url") for l in get_requests if l.get("http_url")])
        potential_scraper = len(get_requests) >= 20 and len(distinct_urls) >= 15

        return Fact(
            timestamp=self.log.timestamp,
            source=source,
            log_level=self.log.log_level or "INFO",
            message=self.log.message or "",
            recent_error_count=len(error_logs),
            recent_warn_count=len(warn_logs),
            repeated_error_count=len(repeated_errors),
            unauthorized_count=len(unauthorized_logs),
            failed_syscall=failed_syscalls,
            matched_pattern=matched_pattern,
            is_silent=is_silent,
            log_frequency_last_minute=len(last_1min),
            potential_scraper=potential_scraper,
            performance_latency=self.log.extra.get("latency", None) if self.log.extra else None,
        )
