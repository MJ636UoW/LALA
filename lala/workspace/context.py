from lala.workspace.models import WorkspaceContext

def format_workspace_prompt_context(ctx: WorkspaceContext) -> str:
    """Formats WorkspaceContext into a clean string block for Orchestrator system prompts."""
    return (
        f"[WORKSPACE INTELLIGENCE CONTEXT]\n"
        f"Root Path: {ctx.root_path}\n"
        f"Project Type: {ctx.project_type.value}\n"
        f"Languages: {', '.join(ctx.languages_detected)}\n"
        f"Git Repository: {'YES' if ctx.git_detected else 'NO'}\n"
        f"Total Files: {ctx.total_files} | Python Files: {ctx.python_files_count} | Tests: {ctx.tests_count}\n"
        f"Config Files: {', '.join(ctx.config_files[:5])}"
    )
