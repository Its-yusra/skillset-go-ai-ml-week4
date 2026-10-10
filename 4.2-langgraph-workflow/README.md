# Task 4.2: Multi-Step Workflow in LangGraph

## Overview

This project demonstrates a multi-step workflow built using LangGraph. It processes user questions through multiple nodes and uses conditional routing to select the appropriate processing path.

## Features

* Shared state management using TypedDict
* Multiple processing nodes
* Simple and complex question routing
* Conditional edges
* Answer validation
* Recovery handling for invalid questions
* Workflow visualization using Mermaid

## Technologies

* Python
* LangGraph
* TypedDict

## Workflow

1. Analyze the user's question.
2. Classify it as simple or complex.
3. Route it to the appropriate processing node.
4. Validate the generated response.
5. Return the result or use the recovery node.

## How to Run

Install the dependency:

```bash
pip install langgraph
```

Run the application:

```bash
python workflow.py
```

## Deliverables

* `workflow.py`: Workflow implementation
* `workflow_diagram.md`: Workflow diagram
* `README.md`: Project documentation

## Note

This version demonstrates LangGraph workflow orchestration and conditional routing. The processing nodes use predefined responses; they do not yet generate answers using an LLM.
