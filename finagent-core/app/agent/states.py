from typing import TypedDict, Annotated
from langgraph.graph import add_messages
from datetime import datetime


class AgentState(TypedDict):
    """Agent状态定义"""
    messages: Annotated[list, add_messages]
    scenario: str
    user_id: str
    session_id: str
    trace_id: str
    context: dict
    current_node: str
    safety_result: dict
    rag_results: list
    final_answer: str
    blocked: bool
    human_intervention: bool


def create_initial_state(
    scenario: str,
    user_id: str,
    session_id: str,
    trace_id: str,
    message: str,
) -> AgentState:
    return AgentState(
        messages=[{"role": "user", "content": message}],
        scenario=scenario,
        user_id=user_id,
        session_id=session_id,
        trace_id=trace_id,
        context={},
        current_node="start",
        safety_result={},
        rag_results=[],
        final_answer="",
        blocked=False,
        human_intervention=False,
    )