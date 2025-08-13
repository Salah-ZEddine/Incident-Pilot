from typing import List, Optional, Dict
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


ERROR_WINDOW_SEC = 120
WARN_WINDOW_SEC = 300
REPEATED_ERROR_WINDOW_SEC = 120
UNAUTHORIZED_WINDOW_SEC = 300
SCRAPER_WINDOW_SEC = 60

SCRAPER_MIN_GETS = 20
SCRAPER_MIN_DISTINCT_URLS = 15
SILENCE_THRESHOLD_MINUTES = 10

def safe_get_logs(source: str, seconds: int) -> List[Dict]:
    """Fetch logs within given time window, always returns a list."""
    return get_logs_within(source, seconds) or []

class FactGenerator:
    def __init__(self, log: LogModel):
        self.log = log
        self.source = log.source or log.hostname or 'source-not-passed'

    @staticmethod
    def normalize_message(message: str) -> str:
        # Remove ISO timestamps and extra spaces
        return re.sub(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?",
            "",
            message
        ).strip()

    def generate_facts_from_log(self) -> Fact:
        # --- Silence detection (fetch last_seen before updating it) ---
        previous_last_seen = get_last_seen(self.source)
        is_silent = self._detect_silence(previous_last_seen)

        # Push current log to history (after silence detection)
        push_log_history(self.source, self.log.model_dump(mode='json'))
        set_last_seen(self.source, self.log.timestamp)

        # Fetch logs for different windows
        last_2min = safe_get_logs(self.source, ERROR_WINDOW_SEC)
        last_5min = safe_get_logs(self.source, WARN_WINDOW_SEC)
        last_1min = safe_get_logs(self.source, SCRAPER_WINDOW_SEC)

        # Compute facts
        error_count = self._count_logs_by_level(last_2min, "ERROR")
        warn_count = self._count_logs_by_level(last_5min, "WARN")
        repeated_error_count = self._count_repeated_errors(last_2min)
        unauthorized_count = self._count_unauthorized(last_5min)
        failed_syscall = self._has_failed_syscall()
        matched_pattern = self._match_suspicious_pattern()
        potential_scraper = self._detect_scraper(last_1min)
        latency = self._get_latency()

        return Fact(
            timestamp=self.log.timestamp,
            source=self.source,
            log_level=self.log.log_level or "INFO",
            message=self.log.message or "",
            recent_error_count=error_count,
            recent_warn_count=warn_count,
            repeated_error_count=repeated_error_count,
            unauthorized_count=unauthorized_count,
            failed_syscall=failed_syscall,
            matched_pattern=matched_pattern,
            is_silent=is_silent,
            log_frequency_last_minute=len(last_1min),
            potential_scraper=potential_scraper,
            performance_latency=latency
        )

    # === Helper Methods ===

    def _count_logs_by_level(self, logs: List[Dict], level: str) -> int:
        return sum(1 for l in logs if l.get("log_level") == level)

    def _count_repeated_errors(self, logs: List[Dict]) -> int:
        normalized_current = self.normalize_message(self.log.message or "")
        return sum(
            1 for l in logs
            if l.get("log_level") == "ERROR" and
            self.normalize_message(l.get("message") or "") == normalized_current
        )

    def _count_unauthorized(self, logs: List[Dict]) -> int:
        keywords = ["unauthorized", "login failed", "403"]
        return sum(
            1 for l in logs
            if any(k in (l.get("message") or "").lower() for k in keywords)
        )

    def _has_failed_syscall(self) -> bool:
        return bool(
            re.search(
                r"(failed to connect|timeout|connection refused|disk full)",
                self.log.message or "",
                re.IGNORECASE
            )
        )

    def _match_suspicious_pattern(self) -> Optional[str]:
        for pattern in SUSPICIOUS_PATTERNS:
            try:
                if re.search(pattern, self.log.message or "", re.IGNORECASE):
                    return pattern
            except re.error:
                # Skip malformed regex
                continue
        return None

    def _detect_silence(self, last_seen) -> bool:
        if not last_seen:
            return False
        silence_threshold = self.log.timestamp - timedelta(minutes=SILENCE_THRESHOLD_MINUTES)
        return last_seen < silence_threshold

    def _detect_scraper(self, logs: List[Dict]) -> bool:
        get_requests = [l for l in logs if l.get("http_method") == "GET"]
        distinct_urls = {l.get("http_url") for l in get_requests if l.get("http_url")}
        return (
                len(get_requests) >= SCRAPER_MIN_GETS and
                len(distinct_urls) >= SCRAPER_MIN_DISTINCT_URLS
        )

    def _get_latency(self) -> Optional[float]:
        if isinstance(self.log.extra, dict):
            return self.log.extra.get("latency")
        return None
