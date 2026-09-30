"""Factory for instantiating LLMs from different providers."""

from langchain_core.language_models import BaseChatModel
from config import (
    GOOGLE_API_KEY, OPENAI_API_KEY,
    CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN,
    GROQ_API_KEY,
    DEFAULT_LLM, DEFAULT_MODEL,
)


def get_llm(provider: str | None = None, model: str | None = None) -> BaseChatModel:
    """Return a configured LLM for the given provider."""
    provider = (provider or DEFAULT_LLM).lower()
    model = model or DEFAULT_MODEL

    if provider == "groq":
        if not GROQ_API_KEY or GROQ_API_KEY.startswith("your_"):
            raise ValueError(
                "GROQ_API_KEY not set. Get a free key at https://console.groq.com/"
            )
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=model or "openai/gpt-oss-120b",
            api_key=GROQ_API_KEY,
            temperature=0.1,
            max_retries=3,
        )

    elif provider == "gemini":
        if not GOOGLE_API_KEY or GOOGLE_API_KEY.startswith("your_"):
            raise ValueError(
                "GOOGLE_API_KEY not set. Get a free key at https://aistudio.google.com/"
            )
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model if "gemini" in model else "gemini-3.6-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.1,
            max_retries=3,
        )

    elif provider == "openai":
        if not OPENAI_API_KEY or OPENAI_API_KEY.startswith("your_"):
            raise ValueError("OPENAI_API_KEY not set.")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model or "gpt-4o-mini",
            api_key=OPENAI_API_KEY,
            temperature=0.1,
            max_retries=3,
        )

    elif provider == "cloudflare":
        if not CLOUDFLARE_API_TOKEN or CLOUDFLARE_API_TOKEN.startswith("your_"):
            raise ValueError("CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN must be set.")
        from langchain_openai import ChatOpenAI
        cf_model = model if model.startswith("@cf/") else "@cf/meta/llama-3.1-8b-instruct"
        return ChatOpenAI(
            model=cf_model,
            api_key=CLOUDFLARE_API_TOKEN,
            base_url=f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/v1",
            temperature=0.1,
            max_retries=3,
        )

    else:
        raise ValueError(
            f"Unknown provider: '{provider}'. Choose from: groq, gemini, openai, cloudflare"
        )
