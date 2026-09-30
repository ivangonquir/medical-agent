from typing import Annotated, TypedDict, Optional
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    patient_id: Optional[str]
    retrieved_papers: list[dict]
    pdf_context: Optional[str]
    final_answer: Optional[str]
