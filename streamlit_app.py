
import os
from pathlib import Path
from typing import TypedDict

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from langsmith import traceable
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


# --------------------------------------------------
# 1. Load Environment Variables and Cloud Secrets
# --------------------------------------------------

load_dotenv()

try:
    cloud_secrets = dict(st.secrets)
except Exception:
    cloud_secrets = {}

for key in (
    "GROQ_API_KEY",
    "LANGSMITH_API_KEY",
    "LANGSMITH_PROJECT",
    "LANGSMITH_TRACING",
):
    if key in cloud_secrets and not os.getenv(key):
        os.environ[key] = str(cloud_secrets[key])

os.environ.setdefault("LANGSMITH_TRACING", "true")
os.environ.setdefault(
    "LANGSMITH_PROJECT",
    "skillset-go-week4-observability"
)


# --------------------------------------------------
# 2. Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).parent

DOCUMENTS_DIR = BASE_DIR / "documents"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Confirm that this model is available for your Groq account.
GROQ_MODEL = "openai/gpt-oss-20b"

UNAVAILABLE = (
    "I cannot find this information in the provided knowledge base."
)


# --------------------------------------------------
# 3. Load or Create FAISS Knowledge Base
# --------------------------------------------------

@st.cache_resource
def get_vectorstore():

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    faiss_index = VECTORSTORE_DIR / "index.faiss"
    faiss_metadata = VECTORSTORE_DIR / "index.pkl"

    if faiss_index.exists() and faiss_metadata.exists():

        vectorstore = FAISS.load_local(
            str(VECTORSTORE_DIR),
            embeddings,
            allow_dangerous_deserialization=True,
        )

        return vectorstore

    pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            "No PDFs found in the documents folder."
        )

    documents = []

    for pdf_file in pdf_files:

        loader = PyPDFLoader(str(pdf_file))
        documents.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
    )

    chunks = splitter.split_documents(documents)

    if not chunks:
        raise ValueError(
            "No readable text was extracted from the PDFs."
        )

    vectorstore = FAISS.from_documents(
        chunks,
        embeddings,
    )

    VECTORSTORE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    vectorstore.save_local(str(VECTORSTORE_DIR))

    return vectorstore


# --------------------------------------------------
# 4. Knowledge Base Search Tool
# --------------------------------------------------

@tool
def search_knowledge_base(question: str) -> str:
    """Search the local PDF knowledge base for relevant information."""

    vectorstore = get_vectorstore()

    docs = vectorstore.similarity_search(
        question,
        k=4,
    )

    results = []

    for doc in docs:

        source = Path(
            doc.metadata.get("source", "Unknown")
        ).name

        page = doc.metadata.get(
            "page",
            "Unknown",
        )

        results.append(
            f"Source: {source}\n"
            f"Page: {page}\n"
            f"Content: {doc.page_content}"
        )

    return "\n\n".join(results)


# --------------------------------------------------
# 5. LangGraph State
# --------------------------------------------------

class AgentState(TypedDict):
    question: str
    context: str
    answer: str
    status: str


# --------------------------------------------------
# 6. Retrieve Node
# --------------------------------------------------

def retrieve_node(state: AgentState):

    context = search_knowledge_base.invoke(
        {
            "question": state["question"]
        }
    )

    return {
        "context": context
    }


def route_after_retrieval(state: AgentState):

    if state["context"].strip():
        return "generate"

    return "missing"


# --------------------------------------------------
# 7. Generate Answer Node
# --------------------------------------------------

def generate_node(state: AgentState):

    client = Groq(
        api_key=os.environ["GROQ_API_KEY"]
    )

    prompt = f"""
You are a knowledge-base assistant.

Answer ONLY using the supplied context.
Do not invent facts or use outside knowledge.

If the answer is not supported by the context,
reply exactly:

"{UNAVAILABLE}"

Context:
--------------------
{state["context"]}
--------------------

Question:
{state["question"]}

Answer:
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    answer = response.choices[0].message.content or ""

    return {
        "answer": answer.strip()
    }


# --------------------------------------------------
# 8. Validate Node
# --------------------------------------------------

def validate_node(state: AgentState):

    answer = state["answer"].strip()

    if not answer:
        return {
            "answer": UNAVAILABLE,
            "status": "fallback",
        }

    if UNAVAILABLE.lower() in answer.lower():
        return {
            "status": "information_unavailable"
        }

    return {
        "status": "answered"
    }


def route_after_validation(state: AgentState):

    if state["status"] == "fallback":
        return "fallback"

    return "respond"


# --------------------------------------------------
# 9. Missing Information and Fallback Nodes
# --------------------------------------------------

def missing_node(state: AgentState):

    return {
        "answer": UNAVAILABLE,
        "status": "information_unavailable",
    }


def fallback_node(state: AgentState):

    return {
        "answer": UNAVAILABLE,
        "status": "fallback",
    }


def respond_node(state: AgentState):

    return {}


# --------------------------------------------------
# 10. Build LangGraph Workflow
# --------------------------------------------------

def build_graph():

    graph = StateGraph(AgentState)

    graph.add_node(
        "retrieve",
        retrieve_node,
    )

    graph.add_node(
        "generate",
        generate_node,
    )

    graph.add_node(
        "validate",
        validate_node,
    )

    graph.add_node(
        "missing",
        missing_node,
    )

    graph.add_node(
        "fallback",
        fallback_node,
    )

    graph.add_node(
        "respond",
        respond_node,
    )

    graph.add_edge(
        START,
        "retrieve",
    )

    graph.add_conditional_edges(
        "retrieve",
        route_after_retrieval,
        {
            "generate": "generate",
            "missing": "missing",
        },
    )

    graph.add_edge(
        "generate",
        "validate",
    )

    graph.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "fallback": "fallback",
            "respond": "respond",
        },
    )

    graph.add_edge(
        "missing",
        END,
    )

    graph.add_edge(
        "fallback",
        END,
    )

    graph.add_edge(
        "respond",
        END,
    )

    return graph.compile()


agent_graph = build_graph()


# --------------------------------------------------
# 11. LangSmith Tracing
# --------------------------------------------------

@traceable(name="Hosted Capstone AI Knowledge Assistant")
def run_agent(question: str):

    return agent_graph.invoke(
        {
            "question": question,
            "context": "",
            "answer": "",
            "status": "",
        }
    )


# --------------------------------------------------
# 12. Streamlit Web Interface
# --------------------------------------------------

st.set_page_config(
    page_title="AI Knowledge Assistant",
    page_icon="📚",
    layout="centered",
)

st.title("AI Knowledge Assistant")

st.caption(
    "Powered by RAG, LangGraph, FAISS and Groq"
)

st.write(
    "Ask questions about the documents in the knowledge base."
)


# Check API key before accepting questions.

if not os.getenv("GROQ_API_KEY"):

    st.error(
        "GROQ_API_KEY is missing. "
        "Configure it in Streamlit Cloud Secrets or your local .env file."
    )

    st.stop()


# Load the knowledge base.

try:

    with st.spinner("Loading knowledge base..."):

        get_vectorstore()

except Exception as error:

    st.error(
        f"Knowledge base could not be loaded: {error}"
    )

    st.stop()


# Chat history.

if "messages" not in st.session_state:

    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# User input.

question = st.chat_input(
    "Ask a question about your documents..."
)


if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):

        st.markdown(question)


    with st.chat_message("assistant"):

        with st.spinner(
            "Searching documents and generating answer..."
        ):

            try:

                result = run_agent(question)

                answer = result["answer"]

                status = result["status"]

                st.markdown(answer)

                st.caption(
                    f"Workflow status: {status}"
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

            except Exception as error:

                st.error(
                    "The request failed. "
                    "Check your application logs and configuration."
                )

                # Do not display API credentials or full exception
                # details to public visitors.
                print(
                    f"Request failed: {type(error).__name__}: {error}"
                )
