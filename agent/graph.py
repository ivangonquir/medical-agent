"""LangGraph agent graph for the medical assistant."""

import re
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from agent.state import AgentState
from agent.prompts import SYSTEM_PROMPT
from agent.tools.pubmed import search_pubmed
from agent.tools.medrxiv import search_medrxiv
from agent.tools.pdf_parser import search_pdf_content, list_uploaded_pdfs
from memory.patient_memory import query_patient_memory, update_patient_info
from agent.llm_factory import get_llm

MAX_TOOL_ROUNDS = 2

_TOOL_CALL_ARTIFACT_RE = re.compile(
    r"<tool_call>.*?</tool_call>|<tool_calls>.*?</tool_calls>",
    re.DOTALL,
)


def _strip_tool_artifacts(text: str) -> str:
    """Remove raw <tool_call> XML that some models embed in text output."""
    return _TOOL_CALL_ARTIFACT_RE.sub("", text).strip()


def _extract_text(content) -> str:
    """Some models (Gemini) return content as a list of parts instead of a string."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [p.get("text", "") if isinstance(p, dict) else str(p) for p in content]
        return "\n".join(p for p in parts if p)
    return str(content)


def _count_tool_rounds(messages: list) -> int:
    return sum(1 for m in messages if isinstance(m, ToolMessage))


def _collect_tool_results(messages: list) -> str:
    """Concatenate all ToolMessage contents into a readable evidence block."""
    blocks = []
    for m in messages:
        if isinstance(m, ToolMessage):
            blocks.append(m.content)
    return "\n\n---\n\n".join(blocks)


def _invoke_with_backoff(llm, messages, max_retries: int = 4):
    """Invoke with exponential backoff on rate-limit errors."""
    import time
    for attempt in range(max_retries):
        try:
            return llm.invoke(messages)
        except Exception as e:
            msg = str(e)
            is_rate_limit = (
                "429" in msg or "rate limit" in msg.lower() or "RESOURCE_EXHAUSTED" in msg
                or "503" in msg or "UNAVAILABLE" in msg or "high demand" in msg.lower()
            )
            if is_rate_limit and attempt < max_retries - 1:
                match = re.search(r"retry[^0-9]*(\d+)", msg, re.IGNORECASE)
                wait = int(match.group(1)) + 5 if match else (2 ** attempt) * 15
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Max retries exceeded")


ALL_TOOLS = [
    search_pubmed,
    search_medrxiv,
    search_pdf_content,
    list_uploaded_pdfs,
    query_patient_memory,
    update_patient_info,
]


def build_graph(provider: str | None = None, model: str | None = None):
    """Build and compile the LangGraph agent graph."""
    llm = get_llm(provider, model)
    llm_with_tools = llm.bind_tools(ALL_TOOLS, tool_choice="auto")

    def agent_node(state: AgentState) -> dict:
        patient_id = state.get("patient_id", "")
        patient_ctx = ""
        if patient_id:
            from memory.patient_memory import get_patient_context_string
            patient_ctx = get_patient_context_string(patient_id)

        messages = list(state["messages"])
        tool_rounds_done = _count_tool_rounds(messages)

        if tool_rounds_done >= MAX_TOOL_ROUNDS:
            # Build a clean text-only prompt with evidence embedded — no tool history.
            # This avoids any "tool_choice" API conflicts across all providers.
            original_q = next(
                (m.content for m in messages if isinstance(m, HumanMessage)), ""
            )
            evidence = _collect_tool_results(messages)
            synthesis_prompt = (
                f"You searched the medical literature and found the following evidence:\n\n"
                f"{evidence}\n\n"
                f"---\n\n"
                f"Using this evidence, answer the following clinical question with full citations:\n\n"
                f"{original_q}\n\n"
                f"IMPORTANT:\n"
                f"- Do NOT output any XML tags, <tool_call> syntax, JSON, or raw API artifacts.\n"
                f"- Write a complete, detailed answer. Every section below is required.\n\n"
                f"## Clinical Bottom Line\n"
                f"(1-2 sentence direct answer)\n\n"
                f"## Evidence Summary\n"
                f"(Key findings from the retrieved literature with citations)\n\n"
                f"## Evidence Quality\n"
                f"(Rate High/Moderate/Low and explain the reasoning)\n\n"
                f"## Clinical Caveats\n"
                f"(Limitations, contraindications, special populations)\n\n"
                f"## Recommended Action\n"
                f"(Practical next step for the clinician)"
            )
            system = SystemMessage(
                content=SYSTEM_PROMPT.format(patient_context=patient_ctx)
            )
            response = _invoke_with_backoff(
                llm, [system, HumanMessage(content=synthesis_prompt)]
            )
        else:
            system = SystemMessage(
                content=SYSTEM_PROMPT.format(patient_context=patient_ctx)
            )
            if not messages or not isinstance(messages[0], SystemMessage):
                messages = [system] + messages
            try:
                response = _invoke_with_backoff(llm_with_tools, messages)
            except Exception as e:
                # Groq rejects tool calls for some models with "tool_choice is none" even
                # when tools are bound — fall back to a knowledge-based answer.
                if (
                    "tool_use_failed" in str(e)
                    or ("tool choice" in str(e).lower() and "none" in str(e).lower())
                    or ("400" in str(e) and "tool" in str(e).lower())
                    or "failed_generation" in str(e)
                ):
                    original_q = next(
                        (m.content for m in messages if isinstance(m, HumanMessage)), ""
                    )
                    evidence = _collect_tool_results(messages)
                    if evidence:
                        fallback = (
                            f"Using your medical knowledge and these retrieved findings:\n\n{evidence}\n\n"
                            f"Answer this clinical question with full citations:\n\n{original_q}"
                        )
                    else:
                        fallback = original_q
                    response = _invoke_with_backoff(
                        llm, [system, HumanMessage(content=fallback)]
                    )
                else:
                    raise

        return {"messages": [response]}

    def should_continue(state: AgentState) -> str:
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        return END

    tool_node = ToolNode(ALL_TOOLS)

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()


def run_agent(
    question: str,
    patient_id: str | None = None,
    provider: str | None = None,
    model: str | None = None,
    graph=None,
) -> dict:
    """Run a single question through the medical agent."""
    if graph is None:
        graph = build_graph(provider, model)

    initial_state: AgentState = {
        "messages": [HumanMessage(content=question)],
        "patient_id": patient_id or "",
        "retrieved_papers": [],
        "pdf_context": None,
        "final_answer": None,
    }

    result = graph.invoke(initial_state, config={"recursion_limit": 20})
    messages = result["messages"]

    answer = ""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and not getattr(msg, "tool_calls", None):
            answer = _strip_tool_artifacts(_extract_text(msg.content))
            if answer:
                break

    # If no usable answer was extracted (e.g. all AIMessages had tool_calls),
    # fall back to a direct knowledge-based invocation.
    if not answer:
        llm = get_llm(provider, model)
        evidence = _collect_tool_results(messages)
        if evidence:
            fallback = (
                f"Using your medical knowledge and these retrieved findings:\n\n{evidence}\n\n"
                f"Answer this clinical question with full citations:\n\n{question}"
            )
        else:
            fallback = question
        from agent.prompts import SYSTEM_PROMPT
        resp = _invoke_with_backoff(
            llm,
            [SystemMessage(content=SYSTEM_PROMPT.format(patient_context="")),
             HumanMessage(content=fallback)],
        )
        answer = _strip_tool_artifacts(_extract_text(resp.content))

    if patient_id and answer:
        from memory.patient_memory import save_interaction
        save_interaction(patient_id, question, answer)

    return {"answer": answer, "messages": messages, "state": result}
