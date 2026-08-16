import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from lala.core.orchestrator import Orchestrator
from lala.core.state import LanguageCode
from lala.voice.pipeline import VoicePipeline
from lala.automation.models import AutomationMode

console = Console()

def run_cli():
    orchestrator = Orchestrator()
    voice_pipeline = VoicePipeline(orchestrator=orchestrator)
    
    health_status = orchestrator.local_llm_manager.get_status()
    rag_status = orchestrator.rag_manager.get_status()
    auto_mode = orchestrator.automation.policy.mode.value
    active_prov = health_status["health"]["active_provider"]
    status_str = f"[bold green]ONLINE ({active_prov.upper()})[/bold green]" if active_prov != "none" else "[bold red]OFFLINE (Local Brain Unavailable)[/bold red]"
    current_model = orchestrator.local_llm_manager.get_current_model()
    online_status = "[bold green]ENABLED[/bold green]" if orchestrator.intel_manager.is_online_enabled() else "[bold yellow]DISABLED (Off by default)[/bold yellow]"

    banner = (
        f"[bold cyan]🚀 LALA Safe Autonomous Security Platform (Phase 10)[/bold cyan]\n"
        f"──────────────────────────────────────────────────\n"
        f"[green]Automation Mode:[/green] [bold white]{auto_mode}[/bold white] (Default: SAFE) | [green]Cloud Fallback:[/green] [bold yellow]DISABLED[/bold yellow]\n"
        f"[green]Active Model:[/green] [bold white]{current_model}[/bold white] | [green]Status:[/green] {status_str}\n"
        f"[green]Offline RAG Engine:[/green] 100% LOCAL | [green]Indexed Docs:[/green] [bold white]{rag_status['indexed_documents']}[/bold white]\n"
        f"[green]Online Intelligence Mode:[/green] {online_status}\n"
        f"[green]Security Engine:[/green] ENFORCED (Zero Privilege Escalation)\n"
        f"──────────────────────────────────────────────────\n"
        f"[dim]Commands: '/automation status|safe|confirm|manual|dry-run', '/investigate auto <target>', '/rag search', '/exit'[/dim]"
    )
    
    console.print(Panel(banner, border_style="cyan", title="LALA Cybersecurity Autonomous Intelligence Platform"))
    
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

            # Command: /automation status | safe | confirm | manual | dry-run | pause | resume | abort
            if cleaned_input.lower().startswith("/automation"):
                parts = cleaned_input.split()
                sub = parts[1].lower() if len(parts) > 1 else "status"

                if sub == "status":
                    mode = orchestrator.automation.policy.mode.value
                    console.print(Panel(f"Automation Mode: [bold white]{mode}[/bold white]\nPaused: {orchestrator.automation.is_paused}\nMax Actions/Run: 25\nMax Runtime: 300s"))
                elif sub == "safe":
                    orchestrator.automation.set_automation_mode(AutomationMode.SAFE)
                    console.print(Panel("[bold green]Automation Mode set to SAFE. Safe read-only & analysis operations authorized automatically.[/bold green]"))
                elif sub == "confirm":
                    orchestrator.automation.set_automation_mode(AutomationMode.CONFIRM)
                    console.print(Panel("[bold yellow]Automation Mode set to CONFIRM. Confirmation required for modifications.[/bold yellow]"))
                elif sub == "manual":
                    orchestrator.automation.set_automation_mode(AutomationMode.MANUAL)
                    console.print(Panel("[bold red]Automation Mode set to MANUAL. Explicit approval required for every action.[/bold red]"))
                elif sub == "dry-run":
                    orchestrator.automation.executor.dry_run = True
                    console.print(Panel("[bold yellow]Dry-Run Mode ENABLED. All actions will be simulated without modifications.[/bold yellow]"))
                elif sub == "pause":
                    orchestrator.automation.pause()
                    console.print(Panel("[bold yellow]Autonomous Workflow Engine PAUSED.[/bold yellow]"))
                elif sub == "resume":
                    orchestrator.automation.resume()
                    console.print(Panel("[bold green]Autonomous Workflow Engine RESUMED.[/bold green]"))
                continue

            # Command: /investigate auto <target>
            if cleaned_input.lower().startswith("/investigate auto"):
                parts = cleaned_input.split(maxsplit=2)
                target = parts[2] if len(parts) > 2 else "suspicious_file.exe"
                console.print(Panel(f"[bold cyan]Launching Safe Autonomous Investigation on target '{target}'...[/bold cyan]"))
                run = orchestrator.automation.execute_investigation(target=target)

                table = Table(title=f"Autonomous Run Summary: {run.run_id}")
                table.add_column("Step", style="cyan")
                table.add_column("Action", style="yellow")
                table.add_column("Risk Class", style="magenta")
                table.add_column("Status", style="bold green")

                for item in run.executed_actions:
                    table.add_row(str(item["step"]), item["action"], item["risk_class"], "EXECUTED" if item["success"] else item["message"])
                console.print(table)
                continue

            # Command: /rag status | search <q>
            if cleaned_input.lower().startswith("/rag"):
                parts = cleaned_input.split(maxsplit=2)
                sub = parts[1].lower() if len(parts) > 1 else "status"

                if sub == "status":
                    st = orchestrator.rag_manager.get_status()
                    console.print(Panel(f"[bold white]LALA RAG Engine Status[/bold white]\n{st}"))
                elif sub == "search" and len(parts) >= 3:
                    query = parts[2]
                    results = orchestrator.rag_manager.search(query, top_k=8)
                    table = Table(title=f"RAG Search Results: '{query}'")
                    table.add_column("Rank", style="cyan")
                    table.add_column("Document", style="yellow")
                    table.add_column("Score", style="bold green")
                    table.add_column("Excerpt", style="white")

                    for idx, r in enumerate(results, start=1):
                        table.add_row(str(idx), r.document_title, str(r.relevance_score), r.text[:80] + "...")
                    console.print(table)
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
