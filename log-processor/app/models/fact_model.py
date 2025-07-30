from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Fact(BaseModel):
    timestamp: datetime
    source: str
    log_level: str
    message: str
    repeated_error_count: Optional[int] = 0
    recent_error_count: Optional[int] = 0
    recent_warn_count: Optional[int] = 0
    log_frequency_last_minute: Optional[int] = 0
    is_silent: Optional[bool] = False
    matched_pattern: Optional[str] = None
    failed_syscall: Optional[bool] = False
    unauthorized_count: Optional[int] = 0
    potential_scraper: Optional[bool] = False
    performance_latency: Optional[float] = None
