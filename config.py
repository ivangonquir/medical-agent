import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")

DEFAULT_LLM = os.getenv("DEFAULT_LLM", "groq")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openai/gpt-oss-120b")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

PATIENT_MEMORY_DIR = os.getenv("PATIENT_MEMORY_DIR", "./data/patient_memory")
PDF_UPLOAD_DIR = os.getenv("PDF_UPLOAD_DIR", "./data/pdfs")

# PubMed E-utilities base URL
PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# MedRxiv API base URL
MEDRXIV_BASE_URL = "https://api.medrxiv.org/details"

# Maximum papers to retrieve per search
MAX_PUBMED_RESULTS = 5
MAX_MEDRXIV_RESULTS = 5

# Source credibility weights (used to rank papers)
CREDIBILITY_CONFIG = {
    "top_journals": [
        "New England Journal of Medicine", "NEJM",
        "The Lancet", "Lancet",
        "JAMA", "Journal of the American Medical Association",
        "BMJ", "British Medical Journal",
        "Nature Medicine",
        "Annals of Internal Medicine",
        "PLOS Medicine",
        "Cell",
        "Nature",
        "Science",
    ],
    "top_universities": [
        "Harvard", "Stanford", "Johns Hopkins", "Mayo Clinic",
        "Oxford", "Cambridge", "MIT", "UCSF",
        "Columbia", "Yale", "Penn", "Michigan",
        "NIH", "CDC", "WHO",
    ],
    "citation_thresholds": {
        "high": 100,
        "medium": 20,
        "low": 0,
    },
    "weights": {
        "top_journal": 1.5,
        "top_university": 1.3,
        "high_citations": 1.4,
        "medium_citations": 1.2,
        "recency_bonus_years": 3,
    }
}

SUPPORTED_LLMS = {
    "groq": {
        "models": [
            "openai/gpt-oss-120b",   # largest, best quality — supports tool calling
            "openai/gpt-oss-20b",    # faster, lighter — supports tool calling
            "qwen/qwen3.8-27b",      # Qwen alternative — supports tool calling
        ],
        "requires_key": "GROQ_API_KEY",
    },
    "gemini": {
        "models": [
            "gemini-3.6-flash",   # 20 req/day free — very limited
        ],
        "requires_key": "GOOGLE_API_KEY",
    },
    "cloudflare": {
        "models": [
            "@cf/meta/llama-3.1-8b-instruct",
            "@cf/mistral/mistral-7b-instruct-v0.2",
            "@cf/google/gemma-7b-it",
        ],
        "requires_key": "CLOUDFLARE_API_TOKEN",
    },
    "openai": {
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
        "requires_key": "OPENAI_API_KEY",
    },
}
