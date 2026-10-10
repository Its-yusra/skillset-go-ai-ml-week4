
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# 1. Define shared state
class WorkflowState(TypedDict):
    question: str
    question_type: str
    answer: str
    is_valid: bool
    status: str


# 2. Node: Analyze the question
def analyze_question(state: WorkflowState):
    question = state["question"].strip()

    if not question:
        return {
            "question_type": "invalid",
            "status": "Question is empty"
        }

    if len(question.split()) > 8:
        question_type = "complex"
    else:
        question_type = "simple"

    print(f"\n[Analyze] Question type: {question_type}")

    return {
        "question_type": question_type,
        "status": "Question analyzed"
    }


# 3. Node: Handle a simple question
def simple_answer(state: WorkflowState):
    question = state["question"]

    answer = (
        f"Simple question received: {question}. "
        "This workflow has processed your input."
    )

    print("[Simple Node] Processing completed")

    return {
        "answer": answer,
        "status": "Simple processing completed"
    }


# 4. Node: Handle a complex question
def detailed_answer(state: WorkflowState):
    question = state["question"]

    answer = (
        f"Detailed workflow received the question: {question}. "
        "The question has passed through the complex-question path."
    )

    print("[Detailed Node] Processing completed")

    return {
        "answer": answer,
        "status": "Detailed processing completed"
    }


# 5. Node: Validate the answer
def validate_answer(state: WorkflowState):
    answer = state.get("answer", "").strip()
    is_valid = len(answer) >= 10

    print(f"[Validate] Answer valid: {is_valid}")

    return {
        "is_valid": is_valid,
        "status": "Validation completed"
    }


# 6. Node: Recover from a failed validation
def recovery_node(state: WorkflowState):
    print("[Recovery] Preparing fallback response")

    return {
        "answer": (
            "The workflow could not validate its first response. "
            "Please provide a clearer question and try again."
        ),
        "status": "Recovery completed",
        "is_valid": True
    }


# 7. Conditional routing after question analysis
def route_question(state: WorkflowState):
    if state.get("question_type") == "invalid":
        return "recovery"

    if state.get("question_type") == "complex":
        return "detailed"

    return "simple"


# 8. Conditional routing after validation
def route_validation(state: WorkflowState):
    if state.get("is_valid", False):
        return "success"

    return "recovery"


# 9. Build the graph
builder = StateGraph(WorkflowState)

builder.add_node("analyze", analyze_question)
builder.add_node("simple", simple_answer)
builder.add_node("detailed", detailed_answer)
builder.add_node("validate", validate_answer)
builder.add_node("recovery", recovery_node)

builder.add_edge(START, "analyze")

builder.add_conditional_edges(
    "analyze",
    route_question,
    {
        "simple": "simple",
        "detailed": "detailed",
        "recovery": "recovery"
    }
)

builder.add_edge("simple", "validate")
builder.add_edge("detailed", "validate")

builder.add_conditional_edges(
    "validate",
    route_validation,
    {
        "success": END,
        "recovery": "recovery"
    }
)

builder.add_edge("recovery", END)

# 10. Compile the workflow
app = builder.compile()


# 11. Run and test the workflow
if __name__ == "__main__":
    question = input("Enter your question: ")

    initial_state = {
        "question": question,
        "question_type": "",
        "answer": "",
        "is_valid": False,
        "status": "Started"
    }

    result = app.invoke(initial_state)

    print("\n========== FINAL RESULT ==========")
    print("Question type:", result["question_type"])
    print("Answer:", result["answer"])
    print("Status:", result["status"])
    print("Valid:", result["is_valid"])