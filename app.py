"""Streamlit web UI for the Medical Agent."""

import streamlit as st
import os
import tempfile
from pathlib import Path

st.set_page_config(
    page_title="MedAgent — AI Clinical Assistant",
    page_icon="⚕️",
    layout="wide",
)

# --- Session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "graph" not in st.session_state:
    st.session_state.graph = None
if "patient_id" not in st.session_state:
    st.session_state.patient_id = ""
if "provider" not in st.session_state:
    st.session_state.provider = "groq"
if "model" not in st.session_state:
    st.session_state.model = "openai/gpt-oss-120b"


# --- Sidebar ---
with st.sidebar:
    st.title("⚕️ MedAgent")
    st.markdown("*AI Clinical Decision Support*")
    st.divider()

    st.subheader("Patient")
    patient_id = st.text_input("Patient ID", value=st.session_state.patient_id,
                               placeholder="e.g. P001, john_doe")
    if patient_id != st.session_state.patient_id:
        st.session_state.patient_id = patient_id
        st.session_state.messages = []
        st.session_state.graph = None

    if patient_id:
        from memory.patient_memory import load_recent_history, _load_profile
        profile = _load_profile(patient_id)
        if profile.get("conditions"):
            st.caption(f"**Conditions:** {', '.join(profile['conditions'])}")
        if profile.get("medications"):
            st.caption(f"**Medications:** {', '.join(profile['medications'])}")
        if profile.get("allergies"):
            st.caption(f"**Allergies:** {', '.join(profile['allergies'])}")

    st.divider()

    st.subheader("LLM Settings")
    provider = st.selectbox("Provider", ["groq", "gemini", "openai", "cloudflare"],
                            index=["groq", "gemini", "openai", "cloudflare"].index(st.session_state.provider))
    if provider != st.session_state.provider:
        st.session_state.provider = provider
        st.session_state.graph = None

    model_options = {
        "groq": ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"],
        "gemini": ["gemini-3.6-flash"],
        "openai": ["gpt-4o-mini", "gpt-4o"],
        "cloudflare": ["@cf/meta/llama-3.1-8b-instruct", "@cf/mistral/mistral-7b-instruct-v0.2"],
    }
    model = st.selectbox("Model", model_options[provider])
    if model != st.session_state.model:
        st.session_state.model = model
        st.session_state.graph = None

    st.divider()

    st.subheader("Documents")
    if patient_id:
        from memory.patient_memory import _load_profile as _lp
        existing_pdfs = _lp(patient_id).get("uploaded_pdfs", [])
        if existing_pdfs:
            for pdf in existing_pdfs:
                fname = pdf.get("filename", str(pdf)) if isinstance(pdf, dict) else str(pdf)
                st.caption(f"📄 {fname}")
        else:
            st.caption("No documents uploaded yet.")

    uploaded_file = st.file_uploader(
        "Upload a medical document", type=["pdf"],
        key=f"pdf_uploader_{patient_id or 'no_patient'}",
    )
    if uploaded_file and st.button("Ingest PDF"):
        from agent.tools.pdf_parser import ingest_pdf
        from memory.patient_memory import update_patient_profile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        try:
            with st.spinner("Extracting text..."):
                index = ingest_pdf(tmp_path, patient_id or None)
            if patient_id:
                update_patient_profile(patient_id, uploaded_pdfs=[{
                    "pdf_id": index["pdf_id"],
                    "filename": index["filename"],
                }])
            st.success(f"✓ Ingested: {index['filename']} ({index['num_chunks']} chunks)")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            os.unlink(tmp_path)

    st.divider()

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    if patient_id and st.button("Show Patient History"):
        from memory.patient_memory import load_recent_history
        history = load_recent_history(patient_id, n=5)
        for h in history:
            with st.expander(f"{h['timestamp'][:10]} — {h['question'][:60]}"):
                st.write(h["answer"][:500])


# --- Main chat area ---
st.title("⚕️ MedAgent — AI Clinical Decision Support")
st.caption(
    "Evidence-based medical Q&A powered by PubMed, MedRxiv, and your clinical documents. "
    "**Not a substitute for clinical judgment.**"
)

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask a clinical question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching literature and reasoning..."):
            try:
                # Build graph if needed
                if st.session_state.graph is None:
                    from agent.graph import build_graph
                    st.session_state.graph = build_graph(
                        st.session_state.provider,
                        st.session_state.model,
                    )

                from agent.graph import run_agent
                result = run_agent(
                    prompt,
                    patient_id=st.session_state.patient_id or None,
                    graph=st.session_state.graph,
                )
                answer = result["answer"]
            except Exception as e:
                answer = f"**Error:** {e}\n\nPlease check your API key and try again."

        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})


# --- Footer ---
st.divider()
st.caption(
    "⚠️ MedAgent is a research prototype. All outputs require clinical validation. "
    "Do not use for direct patient care without physician review."
)
