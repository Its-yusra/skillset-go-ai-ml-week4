# Capstone Project Report
## AI Knowledge Assistant Using RAG, LangGraph, and LangSmith

**Program:** Skillset-Go EduTech AI/ML Internship  
**Phase:** Week 4 — Applied AI  
**Project Type:** Capstone AI Agent System  
**Developer:** Yusra Komal

---

## 1. Abstract

The AI Knowledge Assistant is a document-based question-answering system that retrieves relevant information from PDF documents and generates answers using a locally running large language model.

The system combines Retrieval-Augmented Generation (RAG), a FAISS vector store, Hugging Face embeddings, Ollama, and LangGraph. LangSmith is used to trace application execution and inspect inputs, outputs, and failures.

The main objective is to build a focused AI assistant that answers questions using the available knowledge base and provides an appropriate response when the requested information cannot be found.

---

## 2. Problem Statement

Finding specific information in lengthy PDF documents can be time-consuming. A conventional document search may require users to manually read multiple pages to locate relevant information.

This project addresses the problem by developing an AI assistant that retrieves relevant document content and uses it to answer user questions.

The system is designed to reduce manual searching while limiting unsupported answers through context-based prompting and basic response validation.

---

## 3. Project Objectives

The main objectives are:

1. Load and process PDF documents.
2. Divide document text into manageable chunks.
3. Generate vector embeddings for semantic retrieval.
4. Store and retrieve document vectors using FAISS.
5. Generate answers using the Ollama Llama 3.2 model.
6. Implement a multi-step workflow using LangGraph.
7. Add a retrieval tool to search the knowledge base.
8. Handle missing information and basic response failures.
9. Monitor application execution through LangSmith.
10. Evaluate the system using normal, multi-part, missing-information, and failure test cases.

---

## 4. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| LangChain | Document processing and integration components |
| LangGraph | Multi-step workflow and conditional routing |
| FAISS | Vector storage and similarity search |
| Hugging Face Embeddings | Convert document text into vector representations |
| Ollama | Run the local language model |
| Llama 3.2 | Generate answers from retrieved context |
| LangSmith | Trace and inspect application execution |
| python-dotenv | Load configuration from environment variables |
| PyPDFLoader | Load PDF documents |

---

## 5. System Architecture

The application follows a retrieval-based question-answering architecture.

### 5.1 Document Processing

PDF files are loaded from the `documents/` directory using `PyPDFLoader`.

The extracted document content is divided into chunks using `RecursiveCharacterTextSplitter`.

The configured chunk size is 800 characters, with an overlap of 100 characters.

### 5.2 Embedding Generation

The Hugging Face embedding model `sentence-transformers/all-MiniLM-L6-v2` converts document chunks into vector representations.

These vectors are used to retrieve text that is semantically relevant to a user's question.

### 5.3 Vector Storage and Retrieval

FAISS stores the document vectors locally.

When a user submits a question, the application performs similarity search and retrieves up to four document chunks.

The retrieved content is passed to the language model as context.

### 5.4 Answer Generation

Ollama runs the `llama3.2` model locally.

The model receives the user's question and retrieved document context. The prompt instructs it to use only the supplied context and return a predefined message when the answer is unavailable.

### 5.5 LangGraph Workflow

The capstone implementation organizes the application into focused nodes:

- **Retrieve:** Search the knowledge base using the retrieval tool.
- **Generate:** Produce an answer using Ollama.
- **Validate:** Check whether the generated answer is empty or indicates unavailable information.
- **Missing:** Return the predefined message when no context is retrieved.
- **Fallback:** Return a fallback response for an empty generated answer.
- **Respond:** Complete the response path.

Conditional routing determines whether the workflow proceeds to generation or returns a missing-information response.

### 5.6 LangSmith Observability

LangSmith tracing is enabled to inspect application runs.

The traces help investigate execution inputs and outputs, observe timing information where available, and identify failures. They support debugging but do not automatically guarantee that every answer is factually correct.

---

## 6. Implementation Details

The application is implemented in Python using two main files.

### 6.1 `rag_app.py`

This file implements the original RAG application, including:

- PDF loading
- Text chunking
- Embedding creation
- FAISS vector-store creation and loading
- Document retrieval
- Answer generation through Ollama

### 6.2 `capstone_agent.py`

This file integrates the existing knowledge base with a LangGraph workflow.

It defines the retrieval tool, shared graph state, workflow nodes, conditional routing, and the main interaction loop.

The application accepts questions through the terminal and displays the generated answer and workflow status.

### 6.3 Configuration

The application loads environment variables through `python-dotenv`.

LangSmith tracing is configured using environment variables for tracing, the API key, and the project name.

API keys and other secrets are excluded from version control.

---

## 7. Workflow Execution

The main execution flow is:

1. The user enters a question.
2. The retrieval tool searches the FAISS knowledge base.
3. The workflow checks whether retrieved context is available.
4. If no context is retrieved, the workflow returns the missing-information message.
5. If context is available, Ollama generates an answer.
6. The validation node checks for an empty answer or the predefined unavailable-information message.
7. The workflow returns the final answer and status.
8. LangSmith traces are inspected to understand execution and investigate failures.

This workflow provides an explicit structure that can be understood and debugged independently of the language model.

---

## 8. Testing and Evaluation

The application should be evaluated using different types of questions and execution conditions.

| Test Case | Purpose | Actual Result | Status |
|---|---|---|---|
| Normal question | Check whether relevant document information is retrieved | [Enter observed result] | [Pass/Fail] |
| Multi-part question | Check whether the answer addresses multiple requested points | [Enter observed result] | [Pass/Fail] |
| Missing-information question | Check handling of information not available in the knowledge base | [Enter observed result] | [Pass/Fail] |
| Runtime failure | Inspect error handling when the model service is unavailable | [Enter observed result] | [Pass/Fail] |

### 8.1 Evaluation Criteria

**Correctness:** Whether the answer agrees with the source document.

**Relevance:** Whether the response addresses the user's question.

**Completeness:** Whether the response covers all requested parts.

**Groundedness:** Whether the answer's factual claims are supported by retrieved content.

**Latency:** The recorded execution time for each tested request.

These criteria should be assessed using actual answers, retrieved chunks, and trace evidence.

### 8.2 Evaluation Summary

**Total tests executed:** [Enter count]

**Tests passed:** [Enter count]

**Tests failed:** [Enter count]

**Observed latency:** [Enter measurements and units]

**Main failure observed:** [Describe the actual issue, or state that no failure was observed during the tested runs]

No performance or accuracy claims should be made without measured results.

---

## 9. Observability with LangSmith

LangSmith is used to inspect traced execution of the capstone application.

The observability process includes:

1. Sending representative questions to the application.
2. Opening the corresponding project traces.
3. Inspecting inputs and outputs.
4. Reviewing intermediate steps where available.
5. Recording latency with the associated test case.
6. Investigating failed runs.
7. Comparing the generated response with the retrieved context.

Screenshots of actual successful and unsuccessful runs should be stored in the project's observability screenshots directory.

The observations should distinguish retrieval problems, generation problems, and infrastructure failures wherever the available trace information supports that distinction.

---

## 10. Error Handling and Limitations

The project has several limitations.

- Retrieval quality depends on the contents and structure of the available PDF documents.
- Similarity search may return chunks that are related to the question but do not contain a complete answer.
- The language model may generate unsupported claims even when instructed to use only retrieved context.
- The current validation node performs basic checks and is not a comprehensive factual verification system.
- An empty retrieval result does not prove that the information is absent from every document; it may reflect a retrieval limitation.
- The application depends on the local Ollama service, an available model, installed dependencies, and a valid vector store.
- LangSmith tracing requires correct configuration and a working connection to the tracing service.
- The terminal application is not a publicly hosted web application.

These limitations should be considered when interpreting test results.

---

## 11. Security and Privacy

The LangSmith API key is stored in a local environment file rather than directly in application code.

The `.env` file must not be committed to GitHub.

Because tracing can transmit application inputs, outputs, and intermediate data to an external service, only appropriate test documents should be used when tracing is enabled.

---

## 12. Future Improvements

Potential improvements include:

- Adding more robust answer validation.
- Improving retrieval quality and document chunking.
- Adding source references to final answers.
- Creating a larger evaluation dataset with reference answers.
- Measuring latency across repeated runs.
- Improving error messages and recovery.
- Developing a web interface for easier interaction.
- Deploying the application if required by the project roadmap.

These are possible future enhancements and are not claimed as implemented features.

---

## 13. Conclusion

The AI Knowledge Assistant brings together document retrieval, local language-model generation, a structured LangGraph workflow, and LangSmith observability.

The project demonstrates how an AI application can be organized into explicit steps for retrieval, generation, validation, and response handling.

Its effectiveness should be judged using the recorded test outcomes, source-document comparisons, and trace evidence. The final evaluation report and screenshots provide supporting evidence of the implemented system and its observed limitations.

---

## 14. Project Evidence

The following evidence should accompany the final submission:

- GitHub repository containing the implementation and setup instructions.
- Architecture diagram matching the implemented workflow.
- Screenshots of successful and unsuccessful LangSmith traces.
- Evaluation report with actual test results and latency measurements.
- Presentation slides summarizing the project and its results.
