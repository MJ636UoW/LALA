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
from lala.agent.executor import MAX_AGENT_STEPS, MAX_TOOL_ITERATIONS

console = Console()

def run_cli():
    orchestrator = Orchestrator()
    voice_pipeline = VoicePipeline(orchestrator=orchestrator)
    
    health_status = orchestrator.local_llm_manager.get_status()
    active_prov = health_status["health"]["active_provider"]
    status_str = f"[bold green]ONLINE ({active_prov.upper()})[/bold green]" if active_prov != "none" else "[bold red]OFFLINE (Local Brain Unavailable)[/bold red]"
    current_model = orchestrator.local_llm_manager.get_current_model()
    online_status = "[bold green]ENABLED[/bold green]" if orchestrator.intel_manager.is_online_enabled() else "[bold yellow]DISABLED (Off by default)[/bold yellow]"

    banner = (
        f"[bold cyan]🚀 LALA Fully Local LLM Runtime & Security Assistant (Phase 8)[/bold cyan]\n"
        f"──────────────────────────────────────────────────\n"
        f"[green]Local LLM Mode:[/green] 100% LOCAL ONLY | [green]Cloud Fallback:[/green] [bold yellow]DISABLED[/bold yellow]\n"
        f"[green]Active Model:[/green] [bold white]{current_model}[/bold white] | [green]Status:[/green] {status_str}\n"
        f"[green]Models Root Directory:[/green] F:\\LALA\\Models\\\n"
        f"[green]Online Intelligence Mode:[/green] {online_status}\n"
        f"[green]Security Engine:[/green] ENFORCED (Zero Privilege Escalation)\n"
        f"──────────────────────────────────────────────────\n"
        f"[dim]Commands: '/model list', '/model current', '/model use <model>', '/model info <model>', '/llm status', '/investigate <IOC>', '/exit'[/dim]"
    )
    
    console.print(Panel(banner, border_style="cyan", title="LALA Local Cybersecurity Platform"))
    
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

            # Command: /model list | current | use <model> | info <model> | health
            if cleaned_input.lower().startswith("/model"):
                parts = cleaned_input.split(maxsplit=2)
                sub = parts[1].lower() if len(parts) > 1 else "list"

                if sub == "list":
                    models = orchestrator.local_llm_manager.list_local_models()
                    table = Table(title="Locally Available Models")
                    table.add_column("Model Name", style="cyan")
                    table.add_column("Provider", style="yellow")
                    table.add_column("Local", style="bold green")
                    table.add_column("Status", style="white")

                    for m in models:
                        table.add_row(m.name, m.provider, "YES" if m.is_local else "NO", m.status)
                    console.print(table)
                elif sub == "current":
                    console.print(Panel(f"Current Local Model: [bold white]{orchestrator.local_llm_manager.get_current_model()}[/bold white]"))
                elif sub == "use" and len(parts) >= 3:
                    new_m = parts[2]
                    orchestrator.local_llm_manager.set_current_model(new_m)
                    console.print(Panel(f"[bold green]Switched active local model to '{new_m}'.[/bold green]"))
                elif sub == "info" and len(parts) >= 3:
                    info = orchestrator.local_llm_manager.get_model_info(parts[2])
                    console.print(Panel(f"[bold white]Model Details: {parts[2]}[/bold white]\n{info.model_dump_json(indent=2)}"))
                elif sub == "health":
                    h = orchestrator.local_llm_manager.health_checker.check_all()
                    console.print(Panel(f"Ollama Health: {h['ollama'].model_dump()}\nLlamaCpp Health: {h['llamacpp'].model_dump()}"))
                continue

            # Command: /llm status
            if cleaned_input.lower() in ["/llm status", "/llm"]:
                st = orchestrator.local_llm_manager.get_status()
                dash = (
                    f"╔══════════════════════════════════════════════════╗\n"
                    f"║            LALA LOCAL AI STATUS (Phase 8)        ║\n"
                    f"╠══════════════════════════════════════════════════╣\n"
                    f"║ Provider    {st['health']['active_provider'].upper()}                              ║\n"
                    f"║ Active Model {st['current_model']}                            ║\n"
                    f"║ Mode        LOCAL ONLY                           ║\n"
                    f"║ Cloud Fallback DISABLED                          ║\n"
                    f"║ Models Root  {st['models_root']}                 ║\n"
                    f"║ Security    ENFORCED                             ║\n"
                    f"╚══════════════════════════════════════════════════╝"
                )
                console.print(Panel(dash, title="Local LLM Status", border_style="cyan"))
                continue

            # Command: /investigate <target>
            if cleaned_input.lower().startswith("/investigate"):
                parts = cleaned_input.split(maxsplit=1)
                target = parts[1] if len(parts) > 1 else "1.1.1.1"
                res = orchestrator.tools.execute_tool("investigate_ioc", target=target)
                out = res.output or {}
                console.print(Panel(
                    f"[bold white]Cybersecurity Investigation Summary[/bold white]\n"
                    f"Case ID: {out.get('case_id')}\nTitle: {out.get('title')}\n"
                    f"Severity: [bold red]{out.get('severity')}[/bold red]\n"
                    f"Risk Score: {out.get('risk_score', {}).get('score')} / 100\n"
                    f"Evidence Items: {out.get('evidence_count')}\n\n"
                    f"Recommendations:\n" + "\n".join(out.get('recommendations', [])),
                    title="Investigation Report", border_style="red"
                ))
                continue

            # Command: /online status | enable | disable
            if cleaned_input.lower().startswith("/online"):
                parts = cleaned_input.split()
                if len(parts) == 1 or parts[1].lower() == "status":
                    st = "ENABLED" if orchestrator.intel_manager.is_online_enabled() else "DISABLED"
                    console.print(Panel(f"Online Intelligence Mode: [bold white]{st}[/bold white]\nUse '/online enable' or '/online disable' to toggle."))
                elif parts[1].lower() == "enable":
                    orchestrator.intel_manager.set_online_enabled(True)
                    console.print(Panel("[bold green]Online Intelligence Mode ENABLED. Approved provider queries authorized.[/bold green]"))
                elif parts[1].lower() == "disable":
                    orchestrator.intel_manager.set_online_enabled(False)
                    console.print(Panel("[bold yellow]Online Intelligence Mode DISABLED. All external network queries blocked.[/bold yellow]"))
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
