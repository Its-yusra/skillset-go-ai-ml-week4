
# Capstone AI Agent Architecture

```mermaid
flowchart TD
    A([User Question]) --> B[Retrieve Node]
    B --> C{Context Available?}
    C -->|Yes| D[Generate Answer with Ollama]
    C -->|No| E[Missing Information Response]
    D --> F[Validate Response]
    F --> G{Answer Empty?}
    G -->|Yes| H[Fallback Response]
    G -->|No| I[Return Final Answer]
    E --> J([End])
    H --> J
    I --> J
```

## Components

- **RAG:** FAISS retrieves relevant PDF chunks.
- **Tool:** `search_knowledge_base` searches the local knowledge base.
- **LLM:** Ollama runs the local Llama 3.2 model.
- **Workflow:** LangGraph controls retrieval, generation, validation and routing.
- **Observability:** LangSmith records traced execution for inspection.
