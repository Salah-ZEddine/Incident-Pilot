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

    def generate_facts_from_log(self: LogModel) -> Fact:
        # Push current log to history
        push_log_history(self.source, self.dict())
        set_last_seen(self.source, self.timestamp)

        # Get logs in past 2min/5min/1min
        last_2min = get_logs_within(self.source, 120)
        last_5min = get_logs_within(self.source, 300)
        last_1min = get_logs_within(self.source, 60)

        # Count occurrences
        error_logs = [l for l in last_2min if l["log_level"] == "ERROR"]
        warn_logs = [l for l in last_5min if l["log_level"] == "WARN"]
        repeated_errors = [
            l for l in last_2min if l["log_level"] == "ERROR" and l["message"] == self.message
        ]
        unauthorized_logs = [
            l for l in last_5min if any(k in l["message"].lower() for k in ["unauthorized", "login failed", "403"])
        ]
        failed_syscalls = any(
            re.search(r"(failed to connect|timeout|connection refused|disk full)", self.message, re.IGNORECASE)
        )

        matched_pattern = next((p for p in SUSPICIOUS_PATTERNS if re.search(p, self.message, re.IGNORECASE)), None)

        # Silence detection
        last_seen = get_last_seen(self.source)
        is_silent = False
        if last_seen:
            silence_threshold = self.timestamp - timedelta(minutes=10)
            is_silent = last_seen < silence_threshold

        # Potential scrapers: too many GETs to different URLs
        get_requests = [l for l in last_1min if l.get("http_method") == "GET"]
        distinct_urls = set([l.get("http_url") for l in get_requests])
        potential_scraper = len(get_requests) >= 20 and len(distinct_urls) >= 15

        return Fact(
            timestamp=self.timestamp,
            source=self.source,
            log_level=self.log_level,
            message=self.message,
            recent_error_count=len(error_logs),
            recent_warn_count=len(warn_logs),
            repeated_error_count=len(repeated_errors),
            unauthorized_count=len(unauthorized_logs),
            failed_syscall=failed_syscalls,
            matched_pattern=matched_pattern,
            is_silent=is_silent,
            log_frequency_last_minute=len(last_1min),
            potential_scraper=potential_scraper,
            performance_latency=self.extra.get("latency", None) if self.extra else None,
        )
