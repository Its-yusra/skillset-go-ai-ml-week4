# AI/ML Knowledge RAG Application

## 1. Project Overview

This project implements a Retrieval-Augmented Generation (RAG) application using LangChain. It allows users to ask questions about a focused collection of PDF documents and receive answers based on retrieved document content.

The application uses local embeddings, FAISS for vector storage and similarity search, and Ollama to generate answers using a locally running language model.

The objective is to build a simple, observable, and cost-free-to-run-without-paid-API-credits RAG prototype.

## 2. Objectives

* Load and process PDF documents.
* Split documents into smaller text chunks.
* Generate embeddings locally.
* Store embeddings in a FAISS vector database.
* Retrieve relevant chunks for user questions.
* Generate answers using retrieved context.
* Test easy, multi-part, unanswerable, and retrieval-focused questions.
* Reduce unsupported answers by instructing the model to use only the provided context.

## 3. Technologies Used

* **Python:** Application development.
* **LangChain:** Document processing and RAG pipeline integration.
* **PyPDF:** PDF document loading.
* **RecursiveCharacterTextSplitter:** Text chunking.
* **Hugging Face Sentence Transformers:** Local text embeddings.
* **FAISS:** Vector storage and similarity search.
* **Ollama:** Local language model execution.
* **Llama 3.2:** Answer generation.

## 4. Project Structure

```text
4.1-rag-application/
├── documents/
│   ├── machine_learning_notes.pdf
│   ├── deep_learning_notes.pdf
│   └── ai_ml_internship_notes.pdf
├── vectorstore/
├── screenshots/
├── rag_app.py
├── requirements.txt
├── architecture.md
├── evaluation_report.md
├── .env
├── .gitignore
└── README.md
```

The PDF filenames above are examples; replace them with the actual filenames in your documents folder. The vectorstore and screenshots folders should contain generated files as applicable.

## 5. System Architecture

```text
PDF Documents
      |
      v
Document Loading
      |
      v
Text Chunking
      |
      v
Local Embeddings
      |
      v
FAISS Vector Store
      |
      v
User Question
      |
      v
Similarity Search
      |
      v
Top 4 Retrieved Chunks
      |
      v
Context-Based Prompt
      |
      v
Local LLM via Ollama
      |
      v
Generated Answer
```

## 6. How the Application Works

### Document Ingestion

The application loads PDF files from the `documents/` directory using PyPDFLoader.

### Text Chunking

The documents are split into smaller chunks using RecursiveCharacterTextSplitter.

* Chunk size: 800 characters
* Chunk overlap: 100 characters

Chunk overlap helps preserve context between neighboring chunks.

### Embeddings

The application uses the `sentence-transformers/all-MiniLM-L6-v2` embedding model through LangChain Hugging Face integrations.

The embeddings are generated locally after the model has been downloaded.

### Vector Store

FAISS stores the document vectors and supports similarity-based retrieval.

The vectorstore is saved locally so it can be reused without recreating the index on every run.

### Retrieval

When a user enters a question, the application retrieves the four most similar document chunks.

The source filename, page number, and retrieved text are displayed so retrieval quality can be inspected.

### Answer Generation

The retrieved chunks are passed to Llama 3.2 through Ollama.

The model is instructed to answer using only the supplied context and to report when the information cannot be found.

These instructions help reduce unsupported answers but do not guarantee that every answer will be correct.

## 7. Installation and Setup

### Prerequisites

* Python 3.13 or another compatible Python version.
* Ollama installed on the computer.
* An internet connection for initial package and model downloads.
* PDF documents placed in the `documents/` directory.

### Step 1: Install Dependencies

Activate the project's virtual environment and run:

```bash
pip install -r requirements.txt
```

### Step 2: Download the Language Model

```bash
ollama pull llama3.2
```

### Step 3: Download and Initialize the Embedding Model

The embedding model is initialized automatically when the application starts. The first run may download model files.

### Step 4: Run the Application

From the `4.1-rag-application/` directory:

```bash
python rag_app.py
```

Enter a question when prompted. Type `exit` to close the application.

## 8. Evaluation and Testing

The application should be evaluated using the following test categories.

| Test                       | Purpose                                               |
| -------------------------- | ----------------------------------------------------- |
| Easy question              | Check retrieval and answer correctness.               |
| Multi-part question        | Check whether all parts are answered.                 |
| Unanswerable question      | Check whether missing information is acknowledged.    |
| Retrieval-focused question | Check whether relevant document chunks are retrieved. |

Actual outputs and observations are recorded in `evaluation_report.md`.

Retrieval quality and generation quality should be evaluated separately. An incorrect answer may result from irrelevant retrieved context or from the language model failing to use relevant context correctly.

## 9. Limitations

* The application currently supports PDF documents.
* Retrieval uses a simple similarity-search strategy.
* The top four chunks may not contain every detail needed for a complex question.
* PDF extraction quality affects retrieval.
* The model may occasionally produce unsupported or incomplete answers.
* The local language model requires sufficient system resources.
* Initial setup requires internet access to download dependencies and model files.
* The application does not guarantee that all unanswerable questions will be declined correctly.

## 10. Future Improvements

* Experiment with chunk size and overlap.
* Improve retrieval quality and relevance.
* Add source citations to generated answers.
* Evaluate groundedness and answer completeness systematically.
* Integrate LangSmith for tracing and evaluation.
* Integrate the RAG application into a LangGraph workflow.

## 11. Conclusion

This project demonstrates the core Retrieval-Augmented Generation workflow: document ingestion, chunking, local embeddings, FAISS vector search, context retrieval, and language-model-based answer generation.

It provides a foundation for building more advanced AI applications involving workflow orchestration, observability, and AI agents.

## 12. Internship Deliverable

**Program:** Skillset Go EduTech — AI/ML Internship

**Week:** 4 — Applied AI Phase

**Task:** 4.1 — RAG Application

**Deliverable:** Working RAG prototype and architecture documentation.
