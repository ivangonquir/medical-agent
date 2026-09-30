"""
Evaluation runner for the medical agent.

Usage:
    python evaluation/run_evaluation.py --provider gemini --model gemini-3.6-flash
    python evaluation/run_evaluation.py --benchmark medqa --n 20
    python evaluation/run_evaluation.py --mini-set
"""

import argparse
import json
import re
import time
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import track

import sys
from pathlib import Path
# Ensure project root is on sys.path when running as evaluation/run_evaluation.py
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

console = Console()


def _extract_mcq_letter(text: str) -> str:
    """Extract A/B/C/D from a free-text MCQ answer robustly."""
    text = text.strip()
    # Direct single letter
    if text and text[0].upper() in "ABCD":
        return text[0].upper()
    # "The answer is B" / "Answer: B" / "**B**" / "(B)"
    m = re.search(r"\b(?:answer\s*(?:is|:)\s*)?[\*\(\[]*([A-D])[\*\)\]]*\b", text, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    return "?"


def run_mini_set_evaluation(provider: str, model: str) -> dict:
    """Run qualitative evaluation on the internal 10-question mini set."""
    from evaluation.mini_set import get_mini_set
    from agent.graph import run_agent, build_graph

    questions = get_mini_set()
    results = []

    console.print(f"\n[bold cyan]Mini-Set Evaluation[/bold cyan] — {provider}/{model}")
    console.print(f"Running {len(questions)} questions...\n")

    graph = build_graph(provider, model)

    for q in track(questions, description="Evaluating..."):
        start = time.time()
        try:
            result = run_agent(q["question"], graph=graph)
            answer = result["answer"]
            latency = round(time.time() - start, 2)
            error = None
        except Exception as e:
            answer = ""
            latency = round(time.time() - start, 2)
            error = str(e)

        results.append({
            "id": q["id"],
            "category": q["category"],
            "question": q["question"],
            "reference": q["reference_answer"],
            "answer": answer,
            "latency_s": latency,
            "error": error,
        })
        time.sleep(8)  # rate limit — each question = ~3 LLM calls

    return {"provider": provider, "model": model, "results": results}


def print_mini_set_results(eval_results: dict):
    console.print("\n[bold green]Results Summary[/bold green]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", width=4)
    table.add_column("Category", width=25)
    table.add_column("Answer Preview", width=60)
    table.add_column("Latency", width=8)
    table.add_column("Error?", width=6)

    for r in eval_results["results"]:
        preview = r["answer"][:80].replace("\n", " ") + ("..." if len(r["answer"]) > 80 else "")
        has_error = "YES" if r["error"] else "no"
        table.add_row(
            r["id"],
            r["category"],
            preview,
            f"{r['latency_s']}s",
            has_error,
        )

    console.print(table)

    # Print full Q&A for manual inspection
    console.print("\n[bold]Full Answers:[/bold]\n")
    for r in eval_results["results"]:
        console.print(f"[cyan]{'='*70}[/cyan]")
        console.print(f"[bold]{r['id']}[/bold] — {r['category']}")
        console.print(f"[yellow]Q:[/yellow] {r['question']}")
        console.print(f"\n[yellow]Reference:[/yellow]\n{r['reference']}")
        console.print(f"\n[green]Agent Answer:[/green]\n{r['answer']}")
        if r["error"]:
            console.print(f"[red]ERROR: {r['error']}[/red]")
        console.print()


def run_medqa_benchmark(provider: str, model: str, n_samples: int = 20, direct: bool = True) -> dict:
    """
    Evaluate on MedQA (USMLE) benchmark subset from Hugging Face.
    Dataset: GBaker/MedQA-USMLE-4-options

    direct=True  → ask the LLM directly (no RAG), matching published benchmark methodology
    direct=False → use the full agent pipeline (RAG + tool calls)
    """
    from agent.graph import run_agent, build_graph

    console.print(f"\n[bold cyan]MedQA Benchmark Evaluation[/bold cyan] — {provider}/{model}")

    try:
        from datasets import load_dataset
        dataset = load_dataset("GBaker/MedQA-USMLE-4-options", split="test")
        console.print(f"Loaded {len(dataset)} test questions. Using first {n_samples}.")
    except Exception as e:
        console.print(f"[red]Could not load MedQA dataset: {e}[/red]")
        console.print("Install with: pip install datasets")
        return {}

    samples = list(dataset.select(range(min(n_samples, len(dataset)))))
    mode_label = "direct" if direct else "RAG"
    console.print(f"Mode: [yellow]{mode_label}[/yellow] ({'no tools' if direct else 'PubMed search enabled'})")

    graph = None if direct else build_graph(provider, model)
    llm = None
    if direct:
        from agent.llm_factory import get_llm
        from langchain_core.messages import SystemMessage, HumanMessage
        llm = get_llm(provider, model)

    correct = 0
    results = []

    for i, sample in enumerate(track(samples, description="Evaluating MedQA...")):
        question_text = sample["question"]
        options = sample["options"]
        correct_answer = sample["answer_idx"]

        options_str = "\n".join(f"{k}. {v}" for k, v in sorted(options.items()))
        prompt = (
            f"{question_text}\n\n"
            f"Options:\n{options_str}\n\n"
            "Reply with ONLY the letter (A, B, C, or D) of the correct answer, "
            "followed by a one-sentence explanation."
        )

        try:
            if direct:
                from langchain_core.messages import SystemMessage, HumanMessage
                resp = llm.invoke([
                    SystemMessage(content="You are a medical expert answering USMLE-style questions."),
                    HumanMessage(content=prompt),
                ])
                answer_text = resp.content if isinstance(resp.content, str) else str(resp.content)
            else:
                result = run_agent(prompt, graph=graph)
                answer_text = result["answer"]

            predicted = _extract_mcq_letter(answer_text.strip())
            is_correct = predicted == correct_answer
        except Exception as e:
            predicted = "?"
            is_correct = False
            answer_text = f"ERROR: {e}"

        if is_correct:
            correct += 1

        results.append({
            "question": question_text[:100],
            "correct_answer": correct_answer,
            "predicted": predicted,
            "correct": is_correct,
            "full_answer": answer_text[:200],
        })

        time.sleep(8)

    accuracy = correct / len(samples) if samples else 0
    console.print(f"\n[bold green]MedQA Accuracy: {accuracy:.1%} ({correct}/{len(samples)})[/bold green]")

    return {
        "provider": provider,
        "model": model,
        "benchmark": "MedQA-USMLE",
        "mode": mode_label,
        "n_samples": len(samples),
        "accuracy": accuracy,
        "correct": correct,
        "results": results,
    }


def run_pubmedqa_benchmark(provider: str, model: str, n_samples: int = 20, direct: bool = True) -> dict:
    """
    Evaluate on PubMedQA benchmark (yes/no/maybe questions from PubMed abstracts).
    Dataset: qiaojin/PubMedQA

    direct=True  → read the provided abstract and answer directly (matches published baselines)
    direct=False → use the full agent pipeline (RAG + PubMed search, ignores provided abstract)
    """
    from agent.graph import run_agent, build_graph

    console.print(f"\n[bold cyan]PubMedQA Benchmark Evaluation[/bold cyan] — {provider}/{model}")

    try:
        from datasets import load_dataset
        dataset = load_dataset("qiaojin/PubMedQA", "pqa_labeled", split="train")
        console.print(f"Loaded {len(dataset)} questions. Using first {n_samples}.")
    except Exception as e:
        console.print(f"[red]Could not load PubMedQA dataset: {e}[/red]")
        return {}

    samples = list(dataset.select(range(min(n_samples, len(dataset)))))
    mode_label = "direct" if direct else "RAG"
    console.print(f"Mode: [yellow]{mode_label}[/yellow] ({'read provided abstract' if direct else 'free PubMed search'})")

    graph = None if direct else build_graph(provider, model)
    llm = None
    if direct:
        from agent.llm_factory import get_llm
        llm = get_llm(provider, model)

    correct = 0
    results = []

    for sample in track(samples, description="Evaluating PubMedQA..."):
        question = sample["question"]
        context = " ".join(sample.get("context", {}).get("sentences", [])[:3])
        label = sample["final_decision"]  # "yes", "no", "maybe"

        prompt = (
            f"Based on the following context, answer the question with 'yes', 'no', or 'maybe'.\n\n"
            f"Context: {context[:500]}\n\nQuestion: {question}\n\n"
            "Reply with ONLY 'yes', 'no', or 'maybe', then a brief explanation."
        )

        try:
            if direct:
                from langchain_core.messages import SystemMessage, HumanMessage
                resp = llm.invoke([
                    SystemMessage(content="You are a medical expert. Answer PubMedQA questions based only on the provided context."),
                    HumanMessage(content=prompt),
                ])
                answer_text = resp.content if isinstance(resp.content, str) else str(resp.content)
            else:
                result = run_agent(prompt, graph=graph)
                answer_text = result["answer"]

            answer_lower = answer_text.lower().strip()
            # Search whole answer for first yes/no/maybe (agent response may start with
            # a section header like "## Clinical Bottom Line" rather than the bare word)
            m = re.search(r"\b(yes|no|maybe)\b", answer_lower)
            predicted = m.group(1) if m else "maybe"
            is_correct = predicted == label
        except Exception as e:
            predicted = "maybe"
            is_correct = False
            answer_text = f"ERROR: {e}"

        if is_correct:
            correct += 1

        results.append({
            "question": question[:100],
            "correct_answer": label,
            "predicted": predicted,
            "correct": is_correct,
        })
        time.sleep(8 if not direct else 2)

    accuracy = correct / len(samples) if samples else 0
    console.print(f"\n[bold green]PubMedQA Accuracy: {accuracy:.1%} ({correct}/{len(samples)})[/bold green]")

    return {
        "provider": provider,
        "model": model,
        "benchmark": "PubMedQA",
        "mode": mode_label,
        "n_samples": len(samples),
        "accuracy": accuracy,
        "correct": correct,
        "results": results,
    }


def compare_llms(benchmark: str = "medqa", n_samples: int = 20) -> None:
    """Compare multiple LLMs on the same benchmark."""
    configs = [
        {"provider": "gemini", "model": "gemini-3.6-flash"},
        {"provider": "gemini", "model": "gemini-2.5-flash"},
    ]

    all_results = []
    for cfg in configs:
        if benchmark == "medqa":
            res = run_medqa_benchmark(cfg["provider"], cfg["model"], n_samples)
        elif benchmark == "pubmedqa":
            res = run_pubmedqa_benchmark(cfg["provider"], cfg["model"], n_samples)
        if res:
            all_results.append(res)
        time.sleep(5)

    if not all_results:
        return

    console.print("\n[bold]LLM Comparison Results:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Provider/Model")
    table.add_column("Benchmark")
    table.add_column("Accuracy")
    table.add_column("N")

    for r in all_results:
        table.add_row(
            f"{r['provider']}/{r['model']}",
            r["benchmark"],
            f"{r['accuracy']:.1%}",
            str(r["n_samples"]),
        )
    console.print(table)


def save_results(results: dict, output_dir: str = "evaluation/results") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    provider = results.get("provider", "unknown")
    model = results.get("model", "unknown").replace("/", "-").replace("@", "")
    benchmark = results.get("benchmark", "mini_set")
    filename = f"{output_dir}/{benchmark}_{provider}_{model}_{ts}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    console.print(f"\nResults saved to: [blue]{filename}[/blue]")
    return filename


def main():
    parser = argparse.ArgumentParser(description="Medical Agent Evaluation")
    parser.add_argument("--provider", default="gemini", help="LLM provider")
    parser.add_argument("--model", default="gemini-3.6-flash", help="Model name")
    parser.add_argument("--mini-set", action="store_true", help="Run mini-set evaluation")
    parser.add_argument("--benchmark", choices=["medqa", "pubmedqa"], help="Run a benchmark")
    parser.add_argument("--compare", action="store_true", help="Compare multiple LLMs")
    parser.add_argument("-n", "--n-samples", type=int, default=20, help="Number of benchmark samples")
    parser.add_argument("--rag", action="store_true", help="Run MedQA with full RAG pipeline (default: direct mode)")
    parser.add_argument("--save", action="store_true", help="Save results to JSON")
    args = parser.parse_args()

    if args.mini_set or (not args.benchmark and not args.compare):
        results = run_mini_set_evaluation(args.provider, args.model)
        if args.save:
            save_results(results)
        print_mini_set_results(results)

    elif args.benchmark == "medqa":
        results = run_medqa_benchmark(args.provider, args.model, args.n_samples, direct=not args.rag)
        if args.save and results:
            save_results(results)

    elif args.benchmark == "pubmedqa":
        results = run_pubmedqa_benchmark(args.provider, args.model, args.n_samples, direct=not args.rag)
        if args.save and results:
            save_results(results)

    elif args.compare:
        compare_llms(args.benchmark or "medqa", args.n_samples)


if __name__ == "__main__":
    main()
