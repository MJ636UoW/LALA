"""
LALA Workspace Intelligence Subsystem.
Provides safe workspace discovery, project type identification, language detection, and context formatting.
"""
from lala.workspace.scanner import WorkspaceScanner
from lala.workspace.models import WorkspaceContext, ProjectType

__all__ = ["WorkspaceScanner", "WorkspaceContext", "ProjectType"]
