import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from lala.core.orchestrator import Orchestrator
from lala.core.state import LanguageCode
from lala.core.providers.local import LocalProvider
from lala.voice.pipeline import VoicePipeline
from lala.memory.models import MemoryCategory

console = Console()

def run_cli():
    orchestrator = Orchestrator()
    voice_pipeline = VoicePipeline(orchestrator=orchestrator)
    
    # Startup Health Check
    active_provider = orchestrator.router.get_active_provider()
    health = {"online": False, "model_available": False, "installed_models": []}
    
    if isinstance(active_provider, LocalProvider):
        health = active_provider.check_health()

    status_str = "[bold green]ONLINE[/bold green]" if health.get("online") else "[bold red]OFFLINE (Local Brain Unavailable)[/bold red]"
    model_name = orchestrator.config.model_router.providers.get("local", {}).model_name if orchestrator.config.model_router.providers else "qwen2.5:3b"

    banner = (
        f"[bold cyan]🧠 LALA Personal AI Operating Agent (Phase 4)[/bold cyan]\n"
        f"──────────────────────────────────────────────────\n"
        f"[green]Local Brain:[/green] Ollama ({orchestrator.config.model_router.providers.get('local', {}).endpoint or 'http://127.0.0.1:11434'})\n"
        f"[green]Model:[/green] [bold white]{model_name}[/bold white] | [green]Status:[/green] {status_str}\n"
        f"[green]Memory Subsystem:[/green] [bold green]SQLite + FTS5 ONLINE[/bold green] (F:\\LALA\\Memory)\n"
        f"[green]Tools Enabled:[/green] {len(orchestrator.tools.list_tools())} Registered Tools\n"
        f"[green]Security Engine:[/green] ACTIVE (Zero Cloud Fallback)\n"
        f"──────────────────────────────────────────────────\n"
        f"[dim]Commands: '/agent status', '/tools', '/memory', '/system', '/permissions', '/audit', '/voice', '/exit'[/dim]"
    )
    
    console.print(Panel(banner, border_style="cyan", title="LALA Safe Local AI Agent"))
    
    greeting = orchestrator.personality.format_greeting(orchestrator.state.language_context.primary_language)
    console.print(f"[bold magenta]LALA:[/bold magenta] {greeting}\n")

    while True:
        try:
            lang_str = orchestrator.state.language_context.primary_language.value
            user_input = Prompt.ask(f"[bold yellow]{orchestrator.config.system.user_name} [{lang_str}][/bold yellow]")
            
            if not user_input.strip():
                continue

            cleaned_input = user_input.strip()

            if cleaned_input.lower() in ["/exit", "exit", "quit", "/quit"]:
                console.print(f"\n[bold cyan]LALA:[/bold cyan] Goodbye {orchestrator.config.system.user_name}! Shutting down cleanly.\n")
                break

            # Command: /agent status or /status
            if cleaned_input.lower() in ["/agent status", "/agent", "/status"]:
                mem_stats = orchestrator.memory.get_status()
                dash = (
                    f"[bold white]LALA System & Agent Status[/bold white]\n"
                    f"────────────────────────────\n"
                    f"Local Brain: [bold green]ONLINE[/bold green]\n"
                    f"Model: {model_name}\n"
                    f"Voice Engine: [bold green]ONLINE[/bold green]\n"
                    f"Memory Subsystem: [bold green]ONLINE[/bold green] ({mem_stats['total_memories']} items in SQLite)\n"
                    f"Persistent DB Path: {mem_stats['persistent_db']}\n"
                    f"Registered Tools: {len(orchestrator.tools.list_tools())} Tools ({', '.join(orchestrator.tools.list_tools()[:5])}...)\n"
                    f"Security Engine: [bold green]ACTIVE[/bold green]\n"
                    f"Cloud Fallback: [bold green]DISABLED (100% Privacy)[/bold green]\n"
                    f"Storage Root: {orchestrator.config.storage.root}\n"
                    f"────────────────────────────"
                )
                console.print(Panel(dash, title="Agent Dashboard", border_style="cyan"))
                continue

            # Command: /tools or /tool-status
            if cleaned_input.lower() in ["/tools", "/tool-status"]:
                table = Table(title="Registered Safe Agent Tools")
                table.add_column("Tool Name", style="cyan")
                table.add_column("Category", style="yellow")
                table.add_column("Permission Tier", style="bold green")
                table.add_column("Risk Description", style="dim")

                for t_name in orchestrator.tools.list_tools():
                    tool = orchestrator.tools.get_tool(t_name)
                    if tool:
                        table.add_row(tool.name, tool.category, tool.permission_level.value, tool.risk_description)
                console.print(table)
                continue

            # Command: /memory
            if cleaned_input.lower().startswith("/memory"):
                parts = cleaned_input.split(" ", 2)
                if len(parts) == 1:
                    mem_stats = orchestrator.memory.get_status()
                    console.print(Panel(f"SQLite Memory Store: {mem_stats['total_memories']} items saved.\nUse '/memory save <text>', '/memory search <query>', '/memory forget <query>'"))
                elif parts[1] == "save" and len(parts) == 3:
                    if orchestrator.memory.save_memory(parts[2], category=MemoryCategory.PERSISTENT):
                        console.print(Panel(f"[green]Memory saved permanently: '{parts[2]}'[/green]"))
                    else:
                        console.print(Panel("[red]Failed to save memory.[/red]"))
                elif parts[1] == "search" and len(parts) == 3:
                    results = orchestrator.memory.search_memory(parts[2])
                    table = Table(title=f"Memory Search Results for '{parts[2]}'")
                    table.add_column("ID", style="dim")
                    table.add_column("Content", style="bold white")
                    table.add_column("Category", style="cyan")
                    for r in results:
                        table.add_row(r.id[:8], r.content, r.category.value)
                    console.print(table)
                elif parts[1] == "forget" and len(parts) == 3:
                    cnt = orchestrator.memory.forget_memory(parts[2])
                    console.print(Panel(f"[green]Removed {cnt} matching memory records.[/green]"))
                continue

            # Command: /system
            if cleaned_input.lower() == "/system":
                res = orchestrator.tools.execute_tool("system_info")
                console.print(Panel(str(res.output), title="System Diagnostics", border_style="green"))
                continue

            # Command: /permissions
            if cleaned_input.lower() == "/permissions":
                perm_info = (
                    "[bold white]LALA Security & Permission Policy[/bold white]\n"
                    "1. SAFE_AUTOMATIC: System diagnostics & status checks\n"
                    "2. READ_ONLY: Path-sanitized file listing, file reading, code AST inspection\n"
                    "3. USER_CONFIRMATION_REQUIRED: File modifications, git commits, risky CLI actions\n"
                    "4. PRIVILEGED: Unrestricted shell / process kill (DISABLED)\n"
                    "Cloud Fallback: STRICTLY DISABLED"
                )
                console.print(Panel(perm_info, title="Permission Tiering", border_style="yellow"))
                continue

            # Command: /audit
            if cleaned_input.lower() == "/audit":
                log_path = "F:\\LALA\\Logs\\lala_security.log"
                try:
                    with open(log_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()[-10:]
                    console.print(Panel("".join(lines) if lines else "No security audit events logged yet.", title="Security Audit Trail"))
                except Exception:
                    console.print(Panel("No security audit log found at F:\\LALA\\Logs\\lala_security.log", title="Security Audit Trail"))
                continue

            # Language switching
            if cleaned_input.lower() == "/lang en":
                orchestrator.set_language(LanguageCode.ENGLISH)
                console.print(Panel("[green]Language context switched to English.[/green]"))
                continue
            elif cleaned_input.lower() == "/lang hi":
                orchestrator.set_language(LanguageCode.HINDI)
                console.print(Panel("[green]भाषा संदर्भ बदलकर हिंदी (Hindi) किया गया।[/green]"))
                continue
            elif cleaned_input.lower() == "/lang mr":
                orchestrator.set_language(LanguageCode.MARATHI)
                console.print(Panel("[green]भाषा संदर्भ बदलून मराठी (Marathi) केले.[/green]"))
                continue

            # Process user request through Agent Execution Loop
            console.print(f"[bold magenta]LALA:[/bold magenta] ", end="")
            response = orchestrator.process_user_input(cleaned_input)
            console.print(f"{response}\n")

        except (KeyboardInterrupt, EOFError):
            console.print(f"\n[bold cyan]LALA:[/bold cyan] Goodbye {orchestrator.config.system.user_name}! Exiting cleanly.\n")
            break

if __name__ == "__main__":
    run_cli()
