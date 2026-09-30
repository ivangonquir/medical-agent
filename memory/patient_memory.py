"""Patient memory system — stores per-patient conversation history, context, and files."""

import json
import os
from datetime import datetime
from pathlib import Path
from langchain_core.tools import tool
from config import PATIENT_MEMORY_DIR


def _patient_dir(patient_id: str) -> Path:
    base = Path(PATIENT_MEMORY_DIR)
    p = base / patient_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def _profile_path(patient_id: str) -> Path:
    return _patient_dir(patient_id) / "profile.json"


def _history_path(patient_id: str) -> Path:
    return _patient_dir(patient_id) / "history.jsonl"


def _load_profile(patient_id: str) -> dict:
    path = _profile_path(patient_id)
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {
        "patient_id": patient_id,
        "created_at": datetime.now().isoformat(),
        "notes": [],
        "conditions": [],
        "medications": [],
        "allergies": [],
        "uploaded_pdfs": [],
        "session_count": 0,
    }


def _save_profile(patient_id: str, profile: dict) -> None:
    with open(_profile_path(patient_id), "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)


def save_interaction(patient_id: str, question: str, answer: str, papers: list[dict] | None = None) -> None:
    """Append a Q&A interaction to the patient's history."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer[:2000],
        "papers_cited": [p.get("title", "") for p in (papers or [])],
    }
    with open(_history_path(patient_id), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    profile = _load_profile(patient_id)
    profile["session_count"] = profile.get("session_count", 0) + 1
    profile["last_interaction"] = entry["timestamp"]
    _save_profile(patient_id, profile)


def load_recent_history(patient_id: str, n: int = 10) -> list[dict]:
    """Load the last n interactions for a patient."""
    path = _history_path(patient_id)
    if not path.exists():
        return []
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries[-n:]


def update_patient_profile(patient_id: str, **kwargs) -> dict:
    """Update patient profile fields (conditions, medications, allergies, notes)."""
    profile = _load_profile(patient_id)
    for key, value in kwargs.items():
        if key in ("conditions", "medications", "allergies", "notes"):
            if isinstance(value, list):
                existing = set(profile.get(key, []))
                existing.update(value)
                profile[key] = sorted(existing)
            elif isinstance(value, str):
                existing = set(profile.get(key, []))
                existing.add(value)
                profile[key] = sorted(existing)
        elif key == "uploaded_pdfs":
            existing = profile.get("uploaded_pdfs", [])
            if isinstance(value, list):
                existing.extend(value)
            else:
                existing.append(value)
            profile["uploaded_pdfs"] = existing
        else:
            profile[key] = value
    _save_profile(patient_id, profile)
    return profile


def get_patient_context_string(patient_id: str) -> str:
    """Build a context string summarizing what we know about the patient."""
    profile = _load_profile(patient_id)
    history = load_recent_history(patient_id, n=5)

    lines = [f"\n## Patient Context (ID: {patient_id})"]

    if profile.get("conditions"):
        lines.append(f"**Known Conditions**: {', '.join(profile['conditions'])}")
    if profile.get("medications"):
        lines.append(f"**Current Medications**: {', '.join(profile['medications'])}")
    if profile.get("allergies"):
        lines.append(f"**Allergies**: {', '.join(profile['allergies'])}")
    if profile.get("notes"):
        lines.append(f"**Clinical Notes**: {'; '.join(profile['notes'][-3:])}")
    if profile.get("uploaded_pdfs"):
        pdf_entries = [
            f"{p['filename']} (pdf_id: {p['pdf_id']})" if isinstance(p, dict) and "pdf_id" in p
            else (p.get("filename", str(p)) if isinstance(p, dict) else str(p))
            for p in profile["uploaded_pdfs"]
        ]
        lines.append(f"**Uploaded Documents**: {', '.join(pdf_entries)}")

    if history:
        lines.append("\n**Recent Questions**:")
        for entry in history[-3:]:
            ts = entry.get("timestamp", "")[:10]
            q = entry.get("question", "")[:120]
            lines.append(f"  - [{ts}] {q}")

    lines.append("")  # trailing newline
    return "\n".join(lines) if len(lines) > 1 else ""


def list_all_patients() -> list[dict]:
    """List all patients in the memory system."""
    base = Path(PATIENT_MEMORY_DIR)
    if not base.exists():
        return []
    patients = []
    for d in base.iterdir():
        if d.is_dir():
            profile = _load_profile(d.name)
            patients.append({
                "patient_id": d.name,
                "session_count": profile.get("session_count", 0),
                "last_interaction": profile.get("last_interaction", ""),
                "conditions": profile.get("conditions", []),
            })
    return patients


# --- LangChain tools ---

@tool
def query_patient_memory(patient_id: str, query: str = "") -> str:
    """Retrieve memory for a specific patient: profile, history, and uploaded files.

    Args:
        patient_id: The patient's unique identifier
        query: Optional keyword to filter relevant history entries
    """
    profile = _load_profile(patient_id)
    history = load_recent_history(patient_id, n=10)

    if query:
        query_lower = query.lower()
        history = [h for h in history if query_lower in h.get("question", "").lower()
                   or query_lower in h.get("answer", "").lower()]

    lines = [f"## Patient Memory: {patient_id}\n"]
    lines.append(f"**Sessions**: {profile.get('session_count', 0)}")
    lines.append(f"**Last seen**: {profile.get('last_interaction', 'never')}")

    if profile.get("conditions"):
        lines.append(f"**Conditions**: {', '.join(profile['conditions'])}")
    if profile.get("medications"):
        lines.append(f"**Medications**: {', '.join(profile['medications'])}")
    if profile.get("allergies"):
        lines.append(f"**Allergies**: {', '.join(profile['allergies'])}")
    if profile.get("notes"):
        lines.append(f"**Notes**: {'; '.join(profile['notes'])}")

    if history:
        lines.append("\n**Relevant History**:")
        for entry in history[-5:]:
            ts = entry.get("timestamp", "")[:10]
            lines.append(f"\n[{ts}] Q: {entry.get('question', '')[:150]}")
            lines.append(f"A: {entry.get('answer', '')[:200]}...")
            if entry.get("papers_cited"):
                lines.append(f"Papers: {', '.join(entry['papers_cited'][:2])}")

    return "\n".join(lines)


@tool
def update_patient_info(patient_id: str, conditions: str = "", medications: str = "",
                        allergies: str = "", note: str = "") -> str:
    """Update a patient's clinical profile (conditions, medications, allergies, notes).

    Args:
        patient_id: The patient's unique identifier
        conditions: Comma-separated medical conditions to add
        medications: Comma-separated medications to add
        allergies: Comma-separated allergies to add
        note: A clinical note to append
    """
    kwargs = {}
    if conditions:
        kwargs["conditions"] = [c.strip() for c in conditions.split(",") if c.strip()]
    if medications:
        kwargs["medications"] = [m.strip() for m in medications.split(",") if m.strip()]
    if allergies:
        kwargs["allergies"] = [a.strip() for a in allergies.split(",") if a.strip()]
    if note:
        kwargs["notes"] = [note.strip()]

    profile = update_patient_profile(patient_id, **kwargs)
    return f"Patient profile updated for {patient_id}: {json.dumps({k: v for k, v in profile.items() if k in kwargs}, indent=2)}"
