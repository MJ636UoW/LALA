from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class ProjectType(str, Enum):
    PYTHON = "PYTHON"
    NODEJS = "NODEJS"
    REACT = "REACT"
    CYBERSECURITY = "CYBERSECURITY"
    UNKNOWN = "UNKNOWN"

class FileTypeCount(BaseModel):
    extension: str
    count: int

class WorkspaceContext(BaseModel):
    root_path: str
    project_type: ProjectType = ProjectType.UNKNOWN
    languages_detected: List[str] = Field(default_factory=list)
    git_detected: bool = False
    total_files: int = 0
    python_files_count: int = 0
    tests_count: int = 0
    config_files: List[str] = Field(default_factory=list)
    security_files: List[str] = Field(default_factory=list)
    statistics: Dict[str, Any] = Field(default_factory=dict)
