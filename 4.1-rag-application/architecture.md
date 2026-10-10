# RAG Application Architecture

```text
PDF Documents
      |
      v
Document Loading (PyPDFLoader)
      |
      v
Text Chunking
(800 characters, 100 overlap)
      |
      v
Local Hugging Face Embeddings
      |
      v
FAISS Vector Store
      |
      v
User Question
      |
      v
Similarity Search (Top 4 Chunks)
      |
      v
Retrieved Context Inspection
      |
      v
Local LLM (Ollama / Llama 3.2)
      |
      v
Grounded Answer
```

## Components

* Ingestion: Load PDF documents using PyPDFLoader.
* Chunking: Split document text into overlapping chunks.
* Embeddings: Convert text into numerical vectors using a local embedding model.
* Vector Store: Store and search vectors using FAISS.
* Retrieval: Retrieve the four most similar chunks for a question.
* Generation: Pass the retrieved context and question to the local LLM.
* Evaluation: Test answer relevance, completeness, and whether the answer is supported by retrieved context.
