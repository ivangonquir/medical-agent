# MedAgent — Open-Source Clinical AI Assistant

An open-source prototype inspired by OpenEvidence: an AI agent for physicians that retrieves and critically appraises medical literature, answers clinical questions, and maintains per-patient memory.

## Architecture

```
medical-agent/
├── agent/
│   ├── graph.py          # LangGraph agent (ReAct loop)
│   ├── state.py          # AgentState (TypedDict)
│   ├── llm_factory.py    # Multi-LLM support (Gemini, OpenAI, Cloudflare)
│   ├── prompts.py        # System prompts
│   └── tools/
│       ├── pubmed.py     # PubMed E-utilities search + credibility scoring
│       ├── medrxiv.py    # MedRxiv preprint search
│       └── pdf_parser.py # PDF ingestion and search
├── memory/
│   └── patient_memory.py # Per-patient memory (profile, history, files)
├── evaluation/
│   ├── mini_set.py       # 10 internal medical questions
│   ├── run_evaluation.py # Evaluation runner (mini-set, MedQA, PubMedQA)
│   └── benchmarks_report.md  # OpenEvidence benchmark analysis
├── app.py                # Streamlit web UI
├── main.py               # CLI entry point
├── config.py             # Configuration
└── requirements.txt
```

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API keys
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

Get a free Gemini API key at: https://aistudio.google.com/

### 3. Run the web UI
```bash
streamlit run app.py
```

### 4. Or use the CLI
```bash
# Interactive chat
python main.py chat --patient P001

# Single question
python main.py ask "What is the first-line treatment for type 2 diabetes?"

# Ingest a PDF
python main.py ingest --pdf patient_report.pdf --patient P001

# List patients
python main.py patients
```

## Evaluation

```bash
# Run 10-question mini-set (qualitative)
python evaluation/run_evaluation.py --mini-set

# Run MedQA benchmark (20 samples)
python evaluation/run_evaluation.py --benchmark medqa -n 20

# Run PubMedQA benchmark
python evaluation/run_evaluation.py --benchmark pubmedqa -n 20

# Compare multiple LLMs
python evaluation/run_evaluation.py --compare --benchmark medqa -n 20

# Save results
python evaluation/run_evaluation.py --benchmark medqa -n 20 --save
```

## Supported LLMs

| Provider   | Models                               | Key Required        |
|-----------|--------------------------------------|---------------------|
| Gemini     | gemini-3.6-flash, gemini-2.5-flash, gemini-2.5-pro | GOOGLE_API_KEY |
| OpenAI     | gpt-4o-mini, gpt-4o                 | OPENAI_API_KEY      |
| Cloudflare | llama-3.1-8b, mistral-7b            | CLOUDFLARE_API_TOKEN |

## Tools

### search_pubmed
Searches PubMed using NCBI E-utilities (free, no API key required for basic use).
Returns papers ranked by a **credibility score** based on:
- Journal prestige (NEJM, Lancet, JAMA, BMJ → ×1.5)
- Institution prestige (Harvard, Stanford, etc. → ×1.3)
- Citation count (>100 citations → ×1.4)
- Recency bonus for papers <3 years old (×1.1)

### search_medrxiv
Searches MedRxiv preprints. Always flagged as unreviewed (×0.7 penalty vs peer-reviewed).

### search_pdf_content / list_uploaded_pdfs
Ingest PDFs and search across them with keyword matching.

### query_patient_memory / update_patient_info
Per-patient memory stored as JSON in `./data/patient_memory/`. Tracks:
- Medical conditions, medications, allergies
- Clinical notes
- Uploaded documents
- Full Q&A history

## Benchmarks

See [evaluation/benchmarks_report.md](evaluation/benchmarks_report.md) for a detailed analysis of all benchmarks used to evaluate OpenEvidence and similar systems.

**Key benchmarks implemented:**
1. **MedQA (USMLE)** — 4-option MCQ from USMLE Step 1-3
2. **PubMedQA** — Yes/no/maybe questions from PubMed abstracts
3. **MMLU Medical** — Broad medical knowledge MCQ
4. **Internal Mini-Set** — 10 curated clinical questions

## Published Baselines

| Model          | MedQA  | MMLU Med | PubMedQA |
|----------------|--------|----------|----------|
| GPT-4          | 87.0%  | 91.1%    | 75.2%    |
| Med-PaLM 2     | 86.5%  | 88.3%    | 79.7%    |
| Gemini 1.5 Pro | 91.1%  | —        | —        |
| GPT-3.5        | 57.0%  | 75.1%    | 74.4%    |

## Disclaimer

MedAgent is a research prototype. All outputs require clinical validation by qualified healthcare professionals. This system is not approved for direct patient care.
