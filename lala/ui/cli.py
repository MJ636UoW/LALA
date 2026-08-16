import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from lala.core.orchestrator import Orchestrator
from lala.core.state import LanguageCode

console = Console()

def run_cli():
    orchestrator = Orchestrator()
    
    greeting = orchestrator.personality.format_greeting(orchestrator.state.language_context.primary_language)
    
    banner = (
        f"[bold cyan]🧠 LALA Personal AI Assistant[/bold cyan]\n"
        f"[green]System Identity:[/green] [bold white]LALA[/bold white] | [green]User:[/green] [bold white]{orchestrator.config.system.user_name}[/bold white]\n"
        f"[yellow]Language Context:[/yellow] [bold blue]English (en) / Hindi (hi) / Marathi (mr)[/bold blue]\n"
        f"[dim]Type '/lang en', '/lang hi', '/lang mr' to switch language, or '/exit' to quit.[/dim]\n"
        f"---"
    )
    
    console.print(Panel(banner, border_style="cyan", title="LALA Foundation (Phase 1)"))
    console.print(f"[bold magenta]LALA:[/bold magenta] {greeting}\n")

    while True:
        try:
            lang_str = orchestrator.state.language_context.primary_language.value
            user_input = Prompt.ask(f"[bold yellow]{orchestrator.config.system.user_name} [{lang_str}][/bold yellow]")
            
            if not user_input.strip():
                continue

            if user_input.strip().lower() in ["/exit", "exit", "quit", "/quit"]:
                console.print(f"\n[bold cyan]LALA:[/bold cyan] Goodbye {orchestrator.config.system.user_name}! Shutting down cleanly.\n")
                break

            # Language switching commands
            if user_input.strip().lower() == "/lang en":
                orchestrator.set_language(LanguageCode.ENGLISH)
                console.print(Panel("[green]Language context switched to English.[/green]"))
                continue
            elif user_input.strip().lower() == "/lang hi":
                orchestrator.set_language(LanguageCode.HINDI)
                console.print(Panel("[green]भाषा संदर्भ बदलकर हिंदी (Hindi) किया गया।[/green]"))
                continue
            elif user_input.strip().lower() == "/lang mr":
                orchestrator.set_language(LanguageCode.MARATHI)
                console.print(Panel("[green]भाषा संदर्भ बदलून मराठी (Marathi) केले. [/green]"))
                continue

            response = orchestrator.process_user_input(user_input)
            console.print(f"[bold magenta]LALA:[/bold magenta] {response}\n")

        except (KeyboardInterrupt, EOFError):
            console.print(f"\n[bold cyan]LALA:[/bold cyan] Goodbye {orchestrator.config.system.user_name}! Exiting cleanly.\n")
            break

if __name__ == "__main__":
    run_cli()
