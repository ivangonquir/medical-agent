"""PDF parsing tool — ingests PDFs and makes them searchable."""

import os
import json
import hashlib
from pathlib import Path
from langchain_core.tools import tool
from config import PDF_UPLOAD_DIR


def _get_pdf_store_path() -> Path:
    path = Path(PDF_UPLOAD_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _pdf_id(filepath: str) -> str:
    return hashlib.md5(filepath.encode()).hexdigest()[:8]


def extract_text_from_pdf(filepath: str) -> str:
    """Extract text from a PDF file using pypdf (fallback: pymupdf)."""
    try:
        import pypdf
        reader = pypdf.PdfReader(filepath)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)
    except Exception:
        pass

    try:
        import fitz  # PyMuPDF
        doc = fitz.open(filepath)
        pages = []
        for page in doc:
            pages.append(page.get_text())
        doc.close()
        return "\n\n".join(pages)
    except Exception as e:
        raise RuntimeError(f"Could not extract text from PDF: {e}")


def _index_path(pdf_id: str) -> Path:
    return _get_pdf_store_path() / f"{pdf_id}_index.json"


def ingest_pdf(filepath: str, patient_id: str | None = None) -> dict:
    """Ingest a PDF and store its extracted text for later querying."""
    filepath = os.path.abspath(filepath)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"PDF not found: {filepath}")

    pdf_id = _pdf_id(filepath)
    index_file = _index_path(pdf_id)

    text = extract_text_from_pdf(filepath)

    # Store chunks (simple 1000-char chunks with 200-char overlap)
    chunk_size = 1000
    overlap = 200
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)

    index = {
        "pdf_id": pdf_id,
        "filepath": filepath,
        "filename": os.path.basename(filepath),
        "patient_id": patient_id,
        "total_chars": len(text),
        "num_chunks": len(chunks),
        "chunks": chunks,
        "full_text_preview": text[:2000],
    }

    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    return index


def _load_pdf_index(pdf_id: str) -> dict | None:
    index_file = _index_path(pdf_id)
    if not index_file.exists():
        return None
    with open(index_file, encoding="utf-8") as f:
        return json.load(f)


def list_patient_pdfs(patient_id: str) -> list[dict]:
    """List all PDFs associated with a patient."""
    store = _get_pdf_store_path()
    pdfs = []
    for f in store.glob("*_index.json"):
        with open(f, encoding="utf-8") as fp:
            idx = json.load(fp)
        if idx.get("patient_id") == patient_id:
            pdfs.append({
                "pdf_id": idx["pdf_id"],
                "filename": idx["filename"],
                "num_chunks": idx["num_chunks"],
            })
    return pdfs


def _simple_keyword_search(chunks: list[str], query: str, top_k: int = 5) -> list[str]:
    """Simple keyword-based chunk retrieval (no embeddings needed)."""
    query_terms = query.lower().split()
    scored = []
    for chunk in chunks:
        chunk_lower = chunk.lower()
        score = sum(chunk_lower.count(term) for term in query_terms)
        scored.append((score, chunk))
    scored.sort(key=lambda x: -x[0])
    return [chunk for score, chunk in scored[:top_k] if score > 0]


@tool
def search_pdf_content(query: str, pdf_id: str = "", patient_id: str = "") -> str:
    """Search through uploaded PDF documents for relevant content.
    PDFs are pre-indexed — do NOT pass a file path. Use pdf_id from the
    patient context or from list_uploaded_pdfs (leave empty to search all).

    Args:
        query: Keywords or question to search for in the PDF(s)
        pdf_id: The pdf_id shown in patient context (NOT a filename or path).
                Leave empty to search all PDFs for this patient.
        patient_id: Only search PDFs belonging to this patient. Leave empty
                    to search across all patients.
    """
    store = _get_pdf_store_path()

    if pdf_id:
        index_files = [_index_path(pdf_id)]
    else:
        all_files = list(store.glob("*_index.json"))
        if patient_id:
            index_files = []
            for f in all_files:
                with open(f, encoding="utf-8") as fp:
                    idx = json.load(fp)
                if idx.get("patient_id") == patient_id:
                    index_files.append(f)
        else:
            index_files = all_files

    if not index_files:
        return "No PDFs have been uploaded yet. Use the ingest_pdf function to add a PDF first."

    results = []
    for index_file in index_files:
        if not index_file.exists():
            continue
        with open(index_file, encoding="utf-8") as f:
            idx = json.load(f)

        relevant_chunks = _simple_keyword_search(idx["chunks"], query)
        if relevant_chunks:
            results.append(
                f"### From: {idx['filename']} (ID: {idx['pdf_id']})\n"
                + "\n---\n".join(relevant_chunks[:3])
            )

    if not results:
        return f"No relevant content found for '{query}' in uploaded PDFs."

    return "## PDF Search Results\n\n" + "\n\n".join(results)


@tool
def list_uploaded_pdfs(patient_id: str = "") -> str:
    """List all uploaded PDFs, optionally filtered by patient ID.

    Args:
        patient_id: Filter by patient (empty = list all PDFs)
    """
    store = _get_pdf_store_path()
    all_pdfs = []
    for f in store.glob("*_index.json"):
        with open(f, encoding="utf-8") as fp:
            idx = json.load(fp)
        if not patient_id or idx.get("patient_id") == patient_id:
            all_pdfs.append(idx)

    if not all_pdfs:
        return "No PDFs uploaded yet."

    lines = ["## Uploaded PDFs\n"]
    for idx in all_pdfs:
        lines.append(
            f"- **{idx['filename']}** (ID: `{idx['pdf_id']}`) — "
            f"patient: {idx.get('patient_id', 'none')}, "
            f"{idx['num_chunks']} chunks, {idx['total_chars']:,} chars"
        )
    return "\n".join(lines)
