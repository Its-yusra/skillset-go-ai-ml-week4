
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langsmith import traceable
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END

import ollama

from rag_app import (
    create_embeddings,
    load_vectorstore,
    VECTORSTORE_DIR,
    OLLAMA_MODEL,
)

# Load environment settings
load_dotenv()

UNAVAILABLE_MESSAGE = (
    "I cannot find this information in the provided knowledge base."
)

# --------------------------------------------------
# Load the existing RAG knowledge base
# --------------------------------------------------

if not VECTORSTORE_DIR.exists():
    raise FileNotFoundError(
        "Vector store not found. Run rag_app.py first "
        "to create the knowledge base."
    )

embeddings = create_embeddings()
vectorstore = load_vectorstore(embeddings)


# --------------------------------------------------
# Tool: Search the knowledge base
# --------------------------------------------------

@tool
def search_knowledge_base(question: str) -> str:
    """Search the local PDF knowledge base for relevant information."""

    docs = vectorstore.similarity_search(question, k=4)

    if not docs:
        return ""

    results = []

    for index, doc in enumerate(docs, start=1):
        source = Path(
            doc.metadata.get("source", "Unknown")
        ).name
        page = doc.metadata.get("page", "Unknown")

        results.append(
            f"Source: {source}\n"
            f"Page: {page}\n"
            f"Content: {doc.page_content}"
        )

    return "\n\n".join(results)


# --------------------------------------------------
# Shared graph state
# --------------------------------------------------

class AgentState(TypedDict):
    question: str
    context: str
    answer: str
    status: str


# --------------------------------------------------
# Node 1: Retrieve information using the tool
# --------------------------------------------------

def retrieve_node(state: AgentState):
    context = search_knowledge_base.invoke(
        {"question": state["question"]}
    )

    return {"context": context}


def route_after_retrieval(state: AgentState):
    if state["context"].strip():
        return "generate"

    return "missing"


# --------------------------------------------------
# Node 2: Generate a grounded answer
# --------------------------------------------------

def generate_node(state: AgentState):
    prompt = f"""
You are a knowledge-base assistant.

Answer ONLY using the supplied context.
Do not invent facts or use outside knowledge.

If the answer is not supported by the context,
reply exactly:
"{UNAVAILABLE_MESSAGE}"

Context:
{state["context"]}

Question:
{state["question"]}

Answer:
"""

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    answer = response["message"]["content"].strip()

    return {"answer": answer}


# --------------------------------------------------
# Node 3: Validate the generated response
# --------------------------------------------------

def validate_node(state: AgentState):
    answer = state["answer"].strip()

    if not answer:
        return {
            "answer": UNAVAILABLE_MESSAGE,
            "status": "fallback",
        }

    if UNAVAILABLE_MESSAGE.lower() in answer.lower():
        return {"status": "information_unavailable"}

    return {"status": "answered"}


def route_after_validation(state: AgentState):
    if state["status"] == "fallback":
        return "fallback"

    return "respond"


# --------------------------------------------------
# Response and fallback nodes
# --------------------------------------------------

def missing_node(state: AgentState):
    return {
        "answer": UNAVAILABLE_MESSAGE,
        "status": "information_unavailable",
    }


def fallback_node(state: AgentState):
    return {
        "answer": UNAVAILABLE_MESSAGE,
        "status": "fallback",
    }


def respond_node(state: AgentState):
    return {}


# --------------------------------------------------
# Build the LangGraph workflow
# --------------------------------------------------

builder = StateGraph(AgentState)

builder.add_node("retrieve", retrieve_node)
builder.add_node("generate", generate_node)
builder.add_node("validate", validate_node)
builder.add_node("missing", missing_node)
builder.add_node("fallback", fallback_node)
builder.add_node("respond", respond_node)

builder.add_edge(START, "retrieve")

builder.add_conditional_edges(
    "retrieve",
    route_after_retrieval,
    {
        "generate": "generate",
        "missing": "missing",
    },
)

builder.add_edge("generate", "validate")

builder.add_conditional_edges(
    "validate",
    route_after_validation,
    {
        "fallback": "fallback",
        "respond": "respond",
    },
)

builder.add_edge("missing", END)
builder.add_edge("fallback", END)
builder.add_edge("respond", END)

agent_graph = builder.compile()


# --------------------------------------------------
# Run and trace the capstone agent
# --------------------------------------------------

@traceable(name="Capstone AI Knowledge Assistant")
def run_agent(question: str):
    return agent_graph.invoke(
        {
            "question": question,
            "context": "",
            "answer": "",
            "status": "",
        }
    )


def main():
    print("=" * 60)
    print("CAPSTONE AI KNOWLEDGE ASSISTANT")
    print("Powered by RAG, LangGraph, Ollama and LangSmith")
    print("=" * 60)

    while True:
        question = input(
            "\nEnter your question (or type 'exit'): "
        ).strip()

        if question.lower() == "exit":
            print("Exiting assistant.")
            break

        if not question:
            print("Please enter a question.")
            continue

        try:
            result = run_agent(question)

            print("\n" + "=" * 60)
            print("FINAL ANSWER")
            print("=" * 60)
            print(result["answer"])
            print("\nStatus:", result["status"])

        except Exception as error:
            print("\nThe request failed.")
            print("Error type:", type(error).__name__)
            print("Check Ollama, the model and the LangSmith trace.")


if __name__ == "__main__":
    main()
