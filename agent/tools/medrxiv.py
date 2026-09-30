"""MedRxiv search tool using the official MedRxiv/BioRxiv API."""

import requests
from datetime import datetime, timedelta
from langchain_core.tools import tool
from config import MEDRXIV_BASE_URL, MAX_MEDRXIV_RESULTS, CREDIBILITY_CONFIG


def _score_preprint(paper: dict) -> float:
    """Score a preprint — always lower than peer-reviewed by default."""
    score = 0.7  # preprints start penalized vs peer-reviewed
    cfg = CREDIBILITY_CONFIG

    affiliations = paper.get("author_corresponding_institution", "").lower()
    year = paper.get("year", 2000)

    for u in cfg["top_universities"]:
        if u.lower() in affiliations:
            score *= cfg["weights"]["top_university"]
            break

    current_year = datetime.now().year
    if current_year - year <= cfg["weights"]["recency_bonus_years"]:
        score *= 1.15

    return round(score, 3)


def _search_medrxiv_api(query: str, max_results: int) -> list[dict]:
    """Use MedRxiv search API (collection endpoint with date range)."""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=365 * 3)).strftime("%Y-%m-%d")

    url = f"{MEDRXIV_BASE_URL}/medrxiv/{start_date}/{end_date}/0/json"

    papers = []
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        collection = data.get("collection", [])

        # Filter by keyword match in title/abstract
        query_terms = query.lower().split()
        for item in collection:
            title = item.get("title", "").lower()
            abstract = item.get("abstract", "").lower()
            combined = title + " " + abstract
            matches = sum(1 for term in query_terms if term in combined)
            if matches >= max(1, len(query_terms) // 2):
                papers.append(item)
            if len(papers) >= max_results * 3:
                break

    except Exception:
        pass

    return papers


def _parse_medrxiv_papers(raw: list[dict]) -> list[dict]:
    papers = []
    for item in raw:
        paper = {}
        paper["title"] = item.get("title", "").strip()
        paper["abstract"] = item.get("abstract", "").strip()
        paper["authors"] = item.get("authors", "")
        paper["doi"] = item.get("doi", "")
        paper["url"] = f"https://www.medrxiv.org/content/{paper['doi']}v1" if paper["doi"] else ""
        paper["journal"] = "medRxiv (preprint)"
        paper["affiliations"] = item.get("author_corresponding_institution", "")

        date_str = item.get("date", "2020-01-01")
        try:
            paper["year"] = int(date_str[:4])
        except (ValueError, IndexError):
            paper["year"] = 2020

        paper["citation_count"] = 0
        paper["source"] = "MedRxiv"
        paper["credibility_score"] = _score_preprint(paper)
        papers.append(paper)

    return sorted(papers, key=lambda x: x["credibility_score"], reverse=True)


@tool
def search_medrxiv(query: str) -> str:
    """Search MedRxiv for recent medical preprints.

    ⚠️ MedRxiv papers are PREPRINTS — not yet peer-reviewed. Treat with caution.
    Use for very recent findings not yet published in journals.

    Args:
        query: Medical search query
    """
    try:
        raw = _search_medrxiv_api(query, MAX_MEDRXIV_RESULTS)
        papers = _parse_medrxiv_papers(raw[:MAX_MEDRXIV_RESULTS])

        if not papers:
            return f"No MedRxiv preprints found for: '{query}'"

        result_lines = [
            f"## MedRxiv Preprints for: '{query}'\n"
            f"⚠️ **These are preprints — not yet peer-reviewed. Use with caution.**\n"
        ]
        for i, p in enumerate(papers, 1):
            result_lines.append(
                f"### [{i}] {p['title']}\n"
                f"**Authors**: {p['authors'][:100]}  \n"
                f"**Institution**: {p['affiliations'][:100]}  \n"
                f"**Date**: {p['year']}  \n"
                f"**Credibility Score**: {p['credibility_score']} (preprint penalty applied)  \n"
                f"**URL**: {p['url']}  \n"
                f"**Abstract**: {p['abstract'][:400]}{'...' if len(p['abstract']) > 400 else ''}  \n"
            )

        return "\n".join(result_lines)

    except Exception as e:
        return f"MedRxiv search error: {str(e)}"
