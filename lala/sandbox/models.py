import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class AnalysisType(str, Enum):
    STATIC = "STATIC"
    DYNAMIC = "DYNAMIC"
    HYBRID = "HYBRID"

class ThreatLevel(str, Enum):
    CLEAN = "CLEAN"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ProcessEvent(BaseModel):
    pid: int
    parent_pid: int
    process_name: str
    command_line: str
    image_path: str
    action: str = "CREATE" # CREATE, TERMINATE, INJECT
    timestamp: float = Field(default_factory=time.time)

class RegistryEvent(BaseModel):
    operation: str # RegSetValue, RegCreateKey, RegDeleteKey
    key_path: str
    value_name: Optional[str] = None
    value_data: Optional[str] = None
    process_name: str = "unknown"
    timestamp: float = Field(default_factory=time.time)

class NetworkPacketEvent(BaseModel):
    protocol: str = "TCP" # TCP, UDP, DNS, HTTP
    source_ip: str
    source_port: int
    dest_ip: str
    dest_port: int
    dns_query: Optional[str] = None
    http_host: Optional[str] = None
    http_path: Optional[str] = None
    bytes_transferred: int = 0
    timestamp: float = Field(default_factory=time.time)

class StaticAnalysisResult(BaseModel):
    file_name: str
    file_path: str
    file_size: int
    md5: str
    sha256: str
    entropy: float # Shannon Entropy (0-8)
    is_packed: bool = False
    file_type: str = "PE32"
    entry_point: Optional[str] = None
    subsystem: Optional[str] = None
    sections: List[Dict[str, Any]] = Field(default_factory=list)
    imports: List[str] = Field(default_factory=list)
    exports: List[str] = Field(default_factory=list)
    yara_matches: List[str] = Field(default_factory=list)
    suspicious_strings: List[str] = Field(default_factory=list)
    threat_level: ThreatLevel = ThreatLevel.CLEAN

class DynamicAnalysisResult(BaseModel):
    file_name: str
    sandbox_id: str
    execution_duration_sec: float
    processes_created: List[ProcessEvent] = Field(default_factory=list)
    registry_mutations: List[RegistryEvent] = Field(default_factory=list)
    network_activity: List[NetworkPacketEvent] = Field(default_factory=list)
    persistence_detected: bool = False
    c2_ip_endpoints: List[str] = Field(default_factory=list)
    threat_level: ThreatLevel = ThreatLevel.CLEAN

class MalwareReport(BaseModel):
    report_id: str
    file_name: str
    analysis_type: AnalysisType
    threat_level: ThreatLevel
    static_results: Optional[StaticAnalysisResult] = None
    dynamic_results: Optional[DynamicAnalysisResult] = None
    summary: str
    created_at: float = Field(default_factory=time.time)
