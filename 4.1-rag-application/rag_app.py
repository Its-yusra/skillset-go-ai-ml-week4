from pathlib import Path
from langsmith import traceable
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

import ollama

load_dotenv()
# --------------------------------------------------
# Paths
# --------------------------------------------------

DOCUMENTS_DIR = Path("documents")
VECTORSTORE_DIR = Path("vectorstore")

OLLAMA_MODEL = "llama3.2"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# --------------------------------------------------
# Load Documents
# --------------------------------------------------

def load_documents():

    documents = []

    pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            "No PDF files found inside the documents folder."
        )

    print("\nLoading documents...")

    for pdf_file in pdf_files:

        print(f"Loading: {pdf_file.name}")

        loader = PyPDFLoader(str(pdf_file))

        documents.extend(loader.load())

    print(f"\nTotal pages loaded: {len(documents)}")

    return documents


# --------------------------------------------------
# Split Documents
# --------------------------------------------------

def split_documents(documents):

    print("\nSplitting documents into chunks...")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = text_splitter.split_documents(documents)

    print(f"Total chunks created: {len(chunks)}")

    return chunks


# --------------------------------------------------
# Create Local Embeddings
# --------------------------------------------------

def create_embeddings():

    print("\nLoading local embedding model...")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    print("Local embeddings ready.")

    return embeddings


# --------------------------------------------------
# Create FAISS Vector Store
# --------------------------------------------------

def create_vectorstore(chunks, embeddings):

    print("\nCreating FAISS vector store...")

    vectorstore = FAISS.from_documents(
        chunks,
        embeddings
    )

    VECTORSTORE_DIR.mkdir(exist_ok=True)

    vectorstore.save_local(
        str(VECTORSTORE_DIR)
    )

    print("FAISS vector store created successfully.")

    return vectorstore


# --------------------------------------------------
# Load Existing Vector Store
# --------------------------------------------------

def load_vectorstore(embeddings):

    print("\nLoading existing FAISS vector store...")

    vectorstore = FAISS.load_local(
        str(VECTORSTORE_DIR),
        embeddings,
        allow_dangerous_deserialization=True
    )

    print("FAISS vector store loaded.")

    return vectorstore


# --------------------------------------------------
# Retrieve Documents
# --------------------------------------------------

@traceable
def retrieve_documents(vectorstore, question):

    print("\n" + "=" * 70)
    print("RETRIEVED CONTEXT")
    print("=" * 70)

    retrieved_docs = vectorstore.similarity_search(
        question,
        k=4
    )

    for i, doc in enumerate(retrieved_docs, start=1):

        print(f"\n--- Chunk {i} ---")

        print(
            f"Source: {doc.metadata.get('source', 'Unknown')}"
        )

        print(
            f"Page: {doc.metadata.get('page', 'Unknown')}"
        )

        print("\nContent:")

        print(doc.page_content[:1000])

    return retrieved_docs


# --------------------------------------------------
# Generate Answer with Local Ollama
# --------------------------------------------------

@traceable
def generate_answer(question, retrieved_docs):

    context = "\n\n".join(
        doc.page_content
        for doc in retrieved_docs
    )

    prompt = f"""
You are a knowledge-base assistant.

Answer the user's question ONLY using the provided context.

Rules:

1. Use only the information provided in the context.
2. Do not use outside knowledge.
3. Do not invent facts.
4. If the answer is not available in the context,
   say exactly:

"I cannot find this information in the provided knowledge base."

5. Keep the answer clear and concise.

Context:
--------------------
{context}
--------------------

Question:
{question}

Answer:
"""

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


# --------------------------------------------------
# Main Application
# --------------------------------------------------

def main():

    print("=" * 70)
    print("AI/ML KNOWLEDGE RAG APPLICATION")
    print("=" * 70)

    print("\nUsing local LLM:", OLLAMA_MODEL)

    print(
        "Using local embeddings:",
        EMBEDDING_MODEL
    )

    # Create local embeddings
    embeddings = create_embeddings()

    # Create or load vector store
    if not VECTORSTORE_DIR.exists():

        print("\nVector store not found.")

        documents = load_documents()

        chunks = split_documents(documents)

        vectorstore = create_vectorstore(
            chunks,
            embeddings
        )

    else:

        vectorstore = load_vectorstore(
            embeddings
        )

    print("\nRAG system is ready.")

    while True:

        question = input(
            "\nEnter your question (or type 'exit'): "
        )

        if question.lower() == "exit":

            print("\nExiting RAG application.")

            break

        retrieved_docs = retrieve_documents(
            vectorstore,
            question
        )

        answer = generate_answer(
            question,
            retrieved_docs
        )

        print("\n" + "=" * 70)
        print("GENERATED ANSWER")
        print("=" * 70)

        print(answer)


if __name__ == "__main__":
    main()