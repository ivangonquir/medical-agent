# MedAgent — Project Requirements

## 1. Research OpenEvidence evaluation benchmarks
- [x] Identify standard medical QA benchmarks (MedQA-USMLE, PubMedQA, MMLU Medical, MedMCQA, BioASQ)
- [x] Document published baselines (GPT-4, Med-PaLM 2, Med-Gemini) with correct citations
- [x] Write benchmarks literature review (`evaluation/benchmarks_report.md`)

## 2. LangGraph agent with multiple LLMs
- [x] LangGraph ReAct agent loop (agent → tools → agent → END)
- [x] Multi-provider LLM factory: Groq, Gemini, OpenAI, Cloudflare (`agent/llm_factory.py`)
- [x] Exponential backoff on rate-limit errors
- [x] Hard cap on tool rounds (MAX_TOOL_ROUNDS = 2) to prevent infinite loops
- [x] Streamlit web UI (`app.py`)

## 3. PubMed and MedRxiv search tools
- [x] PubMed tool via NCBI E-utilities API — no API key required (`agent/tools/pubmed.py`)
- [x] MedRxiv tool for preprints (`agent/tools/medrxiv.py`)
- [x] Credibility scoring: journal prestige × institution × citations × recency

## 4. Evaluate against a benchmark subset
- [x] Internal mini-set: 10 qualitative questions with reference answers (`evaluation/mini_set.py`) — **10/10 answered, 0 knowledge failures** (gpt-oss-20b run after bug fixes)
- [x] MedQA-USMLE direct mode: **70%** (20 questions, gpt-oss-20b)
- [x] MedQA-USMLE RAG mode: **80%** (20 questions, gpt-oss-20b, +10 pp over direct)
- [x] PubMedQA RAG mode: **45%** (20 questions, gpt-oss-20b — not comparable to baselines, see report)
- [x] PubMedQA direct mode: `--rag` flag added to `run_pubmedqa_benchmark`; run without `--rag` for direct (apples-to-apples with baselines)
- [x] Full evaluation report written (`evaluation/results/evaluation_report.md`)

## 5. Compare different LLMs
- [x] Compared `qwen/qwen3.8-27b` (mini-set), `gpt-oss-20b` (MedQA + PubMedQA)
- [x] Compared `gpt-oss-20b` vs `qwen/qwen3.8-27b` on MedQA (direct + RAG) and PubMedQA — see evaluation_report.md Part 5
  ```
  python -m evaluation.run_evaluation --benchmark medqa -n 20 --provider groq --model openai/gpt-oss-120b --save
  python -m evaluation.run_evaluation --benchmark medqa -n 20 --provider groq --model openai/gpt-oss-120b --rag --save
  ```

## 6. PDF parsing
- [x] PDF ingestion via pypdf (fallback: pymupdf) — extracts text, stores JSON index with 1000-char chunks (`agent/tools/pdf_parser.py`)
- [x] Keyword-based chunk retrieval tool (`search_pdf_content`)
- [x] PDF upload via Streamlit sidebar, linked to patient ID

## 7. Per-patient memory system
- [x] Per-patient JSON files in `data/patient_memory/{patient_id}/` (`memory/patient_memory.py`)
- [x] `profile.json`: conditions, medications, allergies, notes, uploaded PDFs
- [x] `history.jsonl`: append-only Q&A log across sessions
- [x] Patient context injected into system prompt at each agent call
- [x] LangChain tools: `query_patient_memory`, `update_patient_info`
