import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from lala.tools.filesystem import is_path_safe
from lala.workspace.models import WorkspaceContext, ProjectType
from lala.utils.logging import logger

class WorkspaceScanner:
    """
    Safe workspace discovery scanner for LALA.
    Uses Phase 4.5 canonical path security (is_path_safe) to prevent unauthorized root scanning.
    """
    def __init__(self, root_path: str = "D:\\LALA"):
        self.root_path = root_path

    def scan(self, target_path: Optional[str] = None) -> WorkspaceContext:
        path_to_scan = target_path or self.root_path
        if not is_path_safe(path_to_scan):
            logger.warning(f"WorkspaceScanner Access Denied: Unsafe path '{path_to_scan}'")
            return WorkspaceContext(
                root_path=path_to_scan,
                project_type=ProjectType.UNKNOWN,
                statistics={"error": "Access Denied: Path outside authorized workspace roots."}
            )

        canonical = os.path.realpath(path_to_scan)
        target = Path(canonical)
        if not target.exists() or not target.is_dir():
            return WorkspaceContext(root_path=canonical, project_type=ProjectType.UNKNOWN)

        git_detected = (target / ".git").exists()
        languages = set()
        config_files = []
        security_files = []
        total_files = 0
        python_files_count = 0
        tests_count = 0

        # Known config file names
        known_configs = ["pyproject.toml", "package.json", "default_config.yaml", ".gitignore", "requirements.txt", "setup.py"]

        for root, dirs, files in os.walk(target):
            # Skip hidden dirs like .git, __pycache__, node_modules
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["__pycache__", "node_modules", "venv"]]
            
            for f in files:
                total_files += 1
                rel_path = os.path.relpath(os.path.join(root, f), canonical)
                f_lower = f.lower()
                rel_lower = rel_path.lower()

                if f_lower.endswith(".py"):
                    python_files_count += 1
                    languages.add("Python")
                    if "test_" in f_lower or "_test" in f_lower or "tests" in rel_lower:
                        tests_count += 1
                elif f_lower.endswith(".yaml") or f_lower.endswith(".yml"):
                    languages.add("YAML")
                elif f_lower.endswith(".md"):
                    languages.add("Markdown")
                elif f_lower.endswith(".js") or f_lower.endswith(".jsx") or f_lower.endswith(".ts") or f_lower.endswith(".tsx"):
                    languages.add("JavaScript/TypeScript")
                elif f_lower.endswith(".html") or f_lower.endswith(".css"):
                    languages.add("Web (HTML/CSS)")

                if f_lower in known_configs:
                    config_files.append(rel_path)

                if "security" in rel_lower or "permissions" in rel_lower or "tools" in rel_lower:
                    security_files.append(rel_path)

        # Determine project type
        project_type = ProjectType.UNKNOWN
        if (target / "pyproject.toml").exists() or (target / "requirements.txt").exists() or python_files_count > 0:
            project_type = ProjectType.PYTHON
        elif (target / "package.json").exists():
            project_type = ProjectType.NODEJS

        return WorkspaceContext(
            root_path=canonical,
            project_type=project_type,
            languages_detected=sorted(list(languages)),
            git_detected=git_detected,
            total_files=total_files,
            python_files_count=python_files_count,
            tests_count=tests_count,
            config_files=config_files,
            security_files=security_files[:10],
            statistics={
                "scanned_at": canonical,
                "is_git_repository": git_detected
            }
        )
