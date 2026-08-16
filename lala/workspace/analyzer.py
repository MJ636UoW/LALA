from lala.workspace.scanner import WorkspaceScanner
from lala.workspace.models import WorkspaceContext

class WorkspaceAnalyzer:
    """Calculates workspace statistics and summary metrics."""
    def __init__(self, scanner: WorkspaceScanner):
        self.scanner = scanner

    def analyze(self, target_path: str = "D:\\LALA") -> WorkspaceContext:
        return self.scanner.scan(target_path)
