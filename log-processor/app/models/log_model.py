from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class LogModel(BaseModel):
    timestamp: datetime
    source: Optional[str]
    hostname: Optional[str]
    log_level: Optional[str]
    message: Optional[str]
    event_type: Optional[str]
    source_ip: Optional[str]
    destination_ip: Optional[str]
    user_id: Optional[str]
    username: Optional[str]
    http_method: Optional[str]
    http_url: Optional[str]
    http_status: Optional[int]
    user_agent: Optional[str]
    tags: List[str] = Field(default_factory=list)
    extra: Dict = Field(default_factory=dict)
    tenant: str = "default"