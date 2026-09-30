"""PubMed search tool using NCBI E-utilities (free, no API key required for basic use)."""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from langchain_core.tools import tool
from config import PUBMED_BASE_URL, NCBI_API_KEY, MAX_PUBMED_RESULTS, CREDIBILITY_CONFIG


def _score_paper(paper: dict) -> float:
    """Score a paper based on credibility signals."""
    score = 1.0
    cfg = CREDIBILITY_CONFIG

    journal = paper.get("journal", "").lower()
    affiliations = paper.get("affiliations", "").lower()
    citations = paper.get("citation_count", 0)
    year = paper.get("year", 2000)

    for j in cfg["top_journals"]:
        if j.lower() in journal:
            score *= cfg["weights"]["top_journal"]
            break

    for u in cfg["top_universities"]:
        if u.lower() in affiliations:
            score *= cfg["weights"]["top_university"]
            break

    if citations >= cfg["citation_thresholds"]["high"]:
        score *= cfg["weights"]["high_citations"]
    elif citations >= cfg["citation_thresholds"]["medium"]:
        score *= cfg["weights"]["medium_citations"]

    current_year = datetime.now().year
    if current_year - year <= cfg["weights"]["recency_bonus_years"]:
        score *= 1.1

    return round(score, 3)


def _fetch_pubmed_ids(query: str, max_results: int) -> list[str]:
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "sort": "relevance",
    }
    if NCBI_API_KEY and not NCBI_API_KEY.startswith("your_"):
        params["api_key"] = NCBI_API_KEY

    resp = requests.get(f"{PUBMED_BASE_URL}/esearch.fcgi", params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("esearchresult", {}).get("idlist", [])


def _fetch_pubmed_details(pmids: list[str]) -> list[dict]:
    if not pmids:
        return []

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract",
    }
    if NCBI_API_KEY and not NCBI_API_KEY.startswith("your_"):
        params["api_key"] = NCBI_API_KEY

    resp = requests.get(f"{PUBMED_BASE_URL}/efetch.fcgi", params=params, timeout=15)
    resp.raise_for_status()

    root = ET.fromstring(resp.content)
    papers = []

    for article in root.findall(".//PubmedArticle"):
        paper = {}

        # PMID
        pmid_el = article.find(".//PMID")
        paper["pmid"] = pmid_el.text if pmid_el is not None else ""
        paper["url"] = f"https://pubmed.ncbi.nlm.nih.gov/{paper['pmid']}/"

        # Title
        title_el = article.find(".//ArticleTitle")
        paper["title"] = (title_el.text or "").strip() if title_el is not None else ""

        # Abstract
        abstract_parts = article.findall(".//AbstractText")
        paper["abstract"] = " ".join(
            (p.text or "") for p in abstract_parts if p.text
        ).strip()

        # Journal
        journal_el = article.find(".//Journal/Title")
        paper["journal"] = journal_el.text if journal_el is not None else ""

        # Year
        year_el = article.find(".//PubDate/Year")
        if year_el is None:
            year_el = article.find(".//PubDate/MedlineDate")
        try:
            paper["year"] = int((year_el.text or "2000")[:4]) if year_el is not None else 2000
        except ValueError:
            paper["year"] = 2000

        # Authors
        authors = []
        for author in article.findall(".//Author"):
            last = author.find("LastName")
            fore = author.find("ForeName")
            if last is not None:
                name = last.text or ""
                if fore is not None:
                    name += f" {fore.text or ''}"
                authors.append(name.strip())
        paper["authors"] = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")

        # Affiliations
        aff_els = article.findall(".//Affiliation")
        paper["affiliations"] = " ".join(a.text or "" for a in aff_els[:3])

        # DOI
        doi_el = article.find(".//ArticleId[@IdType='doi']")
        paper["doi"] = doi_el.text if doi_el is not None else ""

        paper["citation_count"] = 0  # PubMed API doesn't return citation counts
        paper["source"] = "PubMed"
        paper["credibility_score"] = _score_paper(paper)

        papers.append(paper)

    return sorted(papers, key=lambda x: x["credibility_score"], reverse=True)


@tool
def search_pubmed(query: str) -> str:
    """Search PubMed for peer-reviewed medical literature.

    Use this tool to find relevant clinical studies, systematic reviews, and
    meta-analyses on medical topics. Returns top papers with abstracts,
    ranked by credibility (journal prestige, institution, recency).

    Args:
        query: Medical search query (e.g. "metformin type 2 diabetes HbA1c reduction RCT")
    """
    try:
        pmids = _fetch_pubmed_ids(query, MAX_PUBMED_RESULTS)
        if not pmids:
            return f"No PubMed results found for: '{query}'"

        papers = _fetch_pubmed_details(pmids)

        result_lines = [f"## PubMed Results for: '{query}'\n"]
        for i, p in enumerate(papers, 1):
            result_lines.append(
                f"### [{i}] {p['title']}\n"
                f"**Authors**: {p['authors']}  \n"
                f"**Journal**: {p['journal']} ({p['year']})  \n"
                f"**Credibility Score**: {p['credibility_score']}  \n"
                f"**URL**: {p['url']}  \n"
                f"**Abstract**: {p['abstract'][:280]}{'...' if len(p['abstract']) > 280 else ''}  \n"
            )

        return "\n".join(result_lines)

    except Exception as e:
        return f"PubMed search error: {str(e)}"


def search_pubmed_raw(query: str) -> list[dict]:
    """Return raw paper dicts (for evaluation scripts)."""
    pmids = _fetch_pubmed_ids(query, MAX_PUBMED_RESULTS)
    return _fetch_pubmed_details(pmids)
