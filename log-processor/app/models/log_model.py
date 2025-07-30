from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


class LogModel(BaseModel):
    timestamp: datetime
    source: Optional[str] = Field(default=None, alias="app_source")
    hostname: Optional[str] = None
    log_level: Optional[str] = Field(default="INFO", alias="level")
    message: Optional[str] = None
    event_type: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    http_method: Optional[str] = None
    http_url: Optional[str] = None
    http_status: Optional[int] = None
    user_agent: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    extra: Dict = Field(default_factory=dict)
    tenant: str = "default"

    @model_validator(mode='before')
    def extract_fields_from_any_structure(cls, values):
        """Handle various log formats and extract relevant fields"""
        if isinstance(values, dict):
            # Create a new dict to avoid modifying the original
            processed = {}
            
            # Handle timestamp
            if 'timestamp' in values:
                processed['timestamp'] = values['timestamp']
            elif '@timestamp' in values:
                processed['timestamp'] = values['@timestamp']
            else:
                processed['timestamp'] = datetime.utcnow().isoformat()
            
            # Handle source (could be app_source, source, service, etc.)
            processed['source'] = (
                values.get('source') or 
                values.get('app_source') or 
                values.get('service') or 
                values.get('container_name') or
                'unknown'
            )
            
            # Handle hostname
            processed['hostname'] = (
                values.get('hostname') or 
                values.get('host') or 
                values.get('container_name') or
                'unknown'
            )
            
            # Handle log level
            processed['log_level'] = (
                values.get('log_level') or 
                values.get('level') or 
                values.get('severity') or
                'INFO'
            )
            
            # Handle message
            processed['message'] = (
                values.get('message') or 
                values.get('msg') or 
                values.get('log') or
                str(values)
            )
            
            # Copy other optional fields if they exist
            optional_fields = [
                'event_type', 'source_ip', 'destination_ip', 'user_id', 
                'username', 'http_method', 'http_url', 'http_status', 'user_agent'
            ]
            
            for field in optional_fields:
                if field in values:
                    processed[field] = values[field]
            
            # Handle tags
            if 'tags' in values:
                processed['tags'] = values['tags'] if isinstance(values['tags'], list) else [values['tags']]
            
            # Store everything else in extra
            extra_data = {}
            for key, value in values.items():
                if key not in processed and key not in ['timestamp', '@timestamp']:
                    extra_data[key] = value
            
            processed['extra'] = extra_data
            processed['tenant'] = values.get('tenant', 'default')
            
            return processed
        
        return values

    @field_validator('timestamp', mode='before')
    def parse_timestamp(cls, v):
        """Parse various timestamp formats"""
        if isinstance(v, str):
            try:
                # Try parsing ISO format with timezone
                from dateutil.parser import isoparse
                return isoparse(v)
            except:
                try:
                    # Fallback to datetime parsing
                    return datetime.fromisoformat(v.replace('Z', '+00:00'))
                except:
                    # Last resort: return current time
                    return datetime.utcnow()
        elif isinstance(v, datetime):
            return v
        else:
            return datetime.utcnow()

    class Config:
        # Allow population by field name or alias
        populate_by_name = True
        # Allow extra fields
        extra = "ignore"