"""CLI entry point for the Medical Agent."""

import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

console = Console()


def chat_loop(patient_id: str, provider: str, model: str):
    """Interactive chat loop."""
    from agent.graph import build_graph, run_agent
    from memory.patient_memory import get_patient_context_string

    console.print(f"\n[bold cyan]Medical Agent[/bold cyan] — {provider}/{model}")
    console.print(f"[dim]Patient: {patient_id or 'anonymous'}[/dim]")
    console.print("[dim]Type 'exit' to quit, 'history' to see patient history[/dim]\n")

    if patient_id:
        ctx = get_patient_context_string(patient_id)
        if ctx:
            console.print(Markdown(ctx))

    graph = build_graph(provider, model)

    while True:
        try:
            question = Prompt.ask("[bold green]You[/bold green]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        if question.strip().lower() in ("exit", "quit", "q"):
            console.print("[dim]Goodbye.[/dim]")
            break

        if question.strip().lower() == "history" and patient_id:
            from memory.patient_memory import load_recent_history
            history = load_recent_history(patient_id, n=5)
            for h in history:
                console.print(f"[dim]{h['timestamp'][:10]}[/dim] {h['question'][:80]}")
            continue

        if not question.strip():
            continue

        with console.status("[bold yellow]Thinking...[/bold yellow]"):
            try:
                result = run_agent(question, patient_id=patient_id, graph=graph)
                answer = result["answer"]
            except Exception as e:
                answer = f"Error: {e}"

        console.print("\n[bold blue]Agent:[/bold blue]")
        console.print(Markdown(answer))
        console.print()


def ingest_pdf_cmd(filepath: str, patient_id: str):
    """Ingest a PDF file."""
    from agent.tools.pdf_parser import ingest_pdf
    from memory.patient_memory import update_patient_profile

    console.print(f"Ingesting: {filepath}")
    try:
        index = ingest_pdf(filepath, patient_id)
        console.print(f"[green]✓[/green] Extracted {index['total_chars']:,} characters, {index['num_chunks']} chunks")
        console.print(f"[green]✓[/green] PDF ID: {index['pdf_id']}")

        if patient_id:
            update_patient_profile(patient_id, uploaded_pdfs=[{
                "pdf_id": index["pdf_id"],
                "filename": index["filename"],
            }])
            console.print(f"[green]✓[/green] Associated with patient: {patient_id}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def list_patients_cmd():
    from memory.patient_memory import list_all_patients
    patients = list_all_patients()
    if not patients:
        console.print("[dim]No patients in memory yet.[/dim]")
        return
    for p in patients:
        console.print(
            f"[cyan]{p['patient_id']}[/cyan] — "
            f"{p['session_count']} sessions, "
            f"last: {p.get('last_interaction', 'never')[:10]}, "
            f"conditions: {', '.join(p['conditions']) or 'none'}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Medical Agent — AI clinical decision support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py chat --patient P001
  python main.py chat --provider gemini --model gemini-2.5-pro
  python main.py ingest --pdf report.pdf --patient P001
  python main.py patients
  python main.py ask "What is the treatment for sepsis?"
        """,
    )

    subparsers = parser.add_subparsers(dest="command")

    # chat command
    chat_p = subparsers.add_parser("chat", help="Start interactive chat")
    chat_p.add_argument("--patient", default="", help="Patient ID")
    chat_p.add_argument("--provider", default="gemini")
    chat_p.add_argument("--model", default="gemini-3.6-flash")

    # ask command (single question)
    ask_p = subparsers.add_parser("ask", help="Ask a single question")
    ask_p.add_argument("question", help="Medical question")
    ask_p.add_argument("--patient", default="")
    ask_p.add_argument("--provider", default="gemini")
    ask_p.add_argument("--model", default="gemini-3.6-flash")

    # ingest command
    ingest_p = subparsers.add_parser("ingest", help="Ingest a PDF")
    ingest_p.add_argument("--pdf", required=True, help="Path to PDF file")
    ingest_p.add_argument("--patient", default="", help="Patient ID to associate")

    # patients command
    subparsers.add_parser("patients", help="List all patients")

    args = parser.parse_args()

    if args.command == "chat":
        chat_loop(args.patient, args.provider, args.model)
    elif args.command == "ask":
        from agent.graph import run_agent
        with console.status("Thinking..."):
            result = run_agent(args.question, patient_id=args.patient,
                               provider=args.provider, model=args.model)
        console.print(Markdown(result["answer"]))
    elif args.command == "ingest":
        ingest_pdf_cmd(args.pdf, args.patient)
    elif args.command == "patients":
        list_patients_cmd()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
