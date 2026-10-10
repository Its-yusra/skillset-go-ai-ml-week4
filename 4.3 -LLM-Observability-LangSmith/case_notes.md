# Task 4.3 — Test Case Notes

## Case 1: Successful RAG Query
- **Input:** what is supervised and unsupervised learning?
- **Observation:** The system retrieved relevant chunks from machine_learning_notes.pdf and generated an answer explaining both learning types.
- **Result:** Pass — The answer was relevant and supported by the retrieved context.

## Case 2: Multi-Part Query
- **Input:** what is the population of Mars?
- **Observation:** The system retrieved unrelated AI/ML content and returned the predefined message: “I cannot find this information in the provided knowledge base.”
- **Result:** Pass — The system declined to answer a question unsupported by the knowledge base.

## Case 3: Missing Information
- **Input:** What is deep learning, and how do CNNs and Transformers work?
- **Observation:** The system retrieved relevant chunks from deep_learning_notes.pdf. The generated answer correctly defined deep learning and explained that CNNs are used for spatial data and computer vision, while Transformers rely on self-attention. However, it did not explain their working mechanisms in detail.
- **Result:** Partially complete. The answer covered all three requested topics, but the explanation of how CNNs and Transformers work was limited.

## Case 4: Failure Handling
- **Input:**What is the difference between FAISS and LangSmith, and how are they used in this RAG application?
- **Observation:** The system retrieved unrelated chunks from the available PDFs and returned the predefined message: “I cannot find this information in the provided knowledge base.” This indicates that the required information was not available in the retrieved context.
- **Result:** Correct refusal. The system avoided generating an unsupported answer.
