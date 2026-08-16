import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from lala.core.orchestrator import Orchestrator
from lala.core.state import LanguageCode
from lala.voice.pipeline import VoicePipeline

console = Console()

def run_cli():
    orchestrator = Orchestrator()
    voice_pipeline = VoicePipeline(orchestrator=orchestrator)
    
    health_status = orchestrator.local_llm_manager.get_status()
    rag_status = orchestrator.rag_manager.get_status()
    active_prov = health_status["health"]["active_provider"]
    status_str = f"[bold green]ONLINE ({active_prov.upper()})[/bold green]" if active_prov != "none" else "[bold red]OFFLINE (Local Brain Unavailable)[/bold red]"
    current_model = orchestrator.local_llm_manager.get_current_model()
    online_status = "[bold green]ENABLED[/bold green]" if orchestrator.intel_manager.is_online_enabled() else "[bold yellow]DISABLED (Off by default)[/bold yellow]"

    banner = (
        f"[bold cyan]🚀 LALA Offline Cybersecurity Knowledge & RAG Platform (Phase 9)[/bold cyan]\n"
        f"──────────────────────────────────────────────────\n"
        f"[green]Local LLM Mode:[/green] 100% LOCAL ONLY | [green]Cloud Fallback:[/green] [bold yellow]DISABLED[/bold yellow]\n"
        f"[green]Active Model:[/green] [bold white]{current_model}[/bold white] | [green]Status:[/green] {status_str}\n"
        f"[green]Offline RAG Engine:[/green] 100% LOCAL | [green]Indexed Docs:[/green] [bold white]{rag_status['indexed_documents']}[/bold white]\n"
        f"[green]Knowledge Root:[/green] F:\\LALA\\Knowledge\\\n"
        f"[green]Online Intelligence Mode:[/green] {online_status}\n"
        f"[green]Security Engine:[/green] ENFORCED (Zero Privilege Escalation)\n"
        f"──────────────────────────────────────────────────\n"
        f"[dim]Commands: '/rag status', '/rag search <query>', '/knowledge add <path>', '/knowledge list', '/model list', '/exit'[/dim]"
    )
    
    console.print(Panel(banner, border_style="cyan", title="LALA Cybersecurity Intelligence Platform"))
    
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

            # Command: /rag status | search <q> | rebuild | clear
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
                elif sub == "rebuild":
                    orchestrator.rag_manager.rebuild_index()
                    console.print(Panel("[bold green]Local RAG index rebuilt successfully.[/bold green]"))
                elif sub == "clear":
                    orchestrator.rag_manager.clear_knowledge_base()
                    console.print(Panel("[bold yellow]Local RAG knowledge base cleared.[/bold yellow]"))
                continue

            # Command: /knowledge add <path> | list | remove <id>
            if cleaned_input.lower().startswith("/knowledge"):
                parts = cleaned_input.split(maxsplit=2)
                sub = parts[1].lower() if len(parts) > 1 else "list"

                if sub == "list":
                    docs = orchestrator.rag_manager.list_knowledge_documents()
                    table = Table(title="Knowledge Base Documents")
                    table.add_column("Doc ID", style="cyan")
                    table.add_column("Title", style="yellow")
                    table.add_column("Path", style="white")
                    table.add_column("Size", style="green")

                    for d in docs:
                        table.add_row(d.get("document_id", "")[:12], d.get("title", ""), d.get("source_path", ""), str(d.get("file_size", 0)))
                    console.print(table)
                elif sub == "add" and len(parts) >= 3:
                    path = parts[2]
                    doc = orchestrator.rag_manager.add_document(path)
                    if doc:
                        console.print(Panel(f"[bold green]Successfully ingested '{doc.title}' into local knowledge base.[/bold green]"))
                    else:
                        console.print(Panel(f"[bold red]Failed to ingest '{path}'. Check path and permissions.[/bold red]"))
                elif sub == "remove" and len(parts) >= 3:
                    doc_id = parts[2]
                    orchestrator.rag_manager.remove_document(doc_id)
                    console.print(Panel(f"[bold yellow]Removed document '{doc_id}' from knowledge base.[/bold yellow]"))
                continue

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
                continue

            # Process user request through Agent Execution Loop with RAG evidence
            console.print(f"[bold magenta]LALA:[/bold magenta] ", end="")
            response = orchestrator.process_user_input(cleaned_input)
            console.print(f"{response}\n")

        except (KeyboardInterrupt, EOFError):
            console.print(f"\n[bold cyan]LALA:[/bold cyan] Goodbye {orchestrator.config.system.user_name}! Exiting cleanly.\n")
            break

if __name__ == "__main__":
    run_cli()
