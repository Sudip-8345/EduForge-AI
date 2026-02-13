from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from config import MAX_REFINEMENT_PASSES
from schemas import GeneratorOutput, ReviewerOutput
from agents.generator import generate_content, refine_content
from agents.reviewer import review_content


class GraphState(TypedDict):
    grade: int
    topic: str
    draft: Optional[GeneratorOutput]
    review: Optional[ReviewerOutput]
    refined: Optional[GeneratorOutput]
    review_refined: Optional[ReviewerOutput]
    pass_number: int


def generate_node(state: GraphState) -> dict:
    result = generate_content(state["grade"], state["topic"])
    return {"draft": result}


def review_node(state: GraphState) -> dict:
    result = review_content(
        grade=state["grade"],
        topic=state["topic"],
        content=state["draft"],
    )
    return {"review": result, "pass_number": state.get("pass_number", 0) + 1}


def refine_node(state: GraphState) -> dict:
    result = refine_content(
        grade=state["grade"],
        topic=state["topic"],
        previous_draft=state["draft"],
        feedback=state["review"].feedback,
    )
    return {"refined": result}


def review_refined_node(state: GraphState) -> dict:
    result = review_content(
        grade=state["grade"],
        topic=state["topic"],
        content=state["refined"],
    )
    return {"review_refined": result}


def should_refine(state: GraphState) -> str:
    review = state["review"]
    pass_number = state.get("pass_number", 1)

    if review.status == "fail" and pass_number <= MAX_REFINEMENT_PASSES:
        return "refine"
    return "done"


def build_graph() -> StateGraph:
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("generate", generate_node)
    workflow.add_node("review", review_node)
    workflow.add_node("refine", refine_node)
    workflow.add_node("review_refined", review_refined_node)

    # Edges
    workflow.set_entry_point("generate")
    workflow.add_edge("generate", "review")

    workflow.add_conditional_edges(
        "review",
        should_refine,
        {
            "refine": "refine",
            "done": END,
        },
    )

    # After refine → review the refined content → end
    workflow.add_edge("refine", "review_refined")
    workflow.add_edge("review_refined", END)

    return workflow.compile()


def run_pipeline(grade: int, topic: str) -> dict:
    graph = build_graph()
    initial_state: GraphState = {
        "grade": grade,
        "topic": topic,
        "draft": None,
        "review": None,
        "refined": None,
        "review_refined": None,
        "pass_number": 0,
    }
    final_state = graph.invoke(initial_state)
    return final_state
