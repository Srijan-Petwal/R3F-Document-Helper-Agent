<div align="center">

<p align="center">
  <img src="r3f-logo.png" alt="React Three Fiber" width="500"/>
</p>

# R3F Document Helper Agent

### A RAG-based agent for working with React Three Fiber documentation.

**RAG · Agents · LangGraph · Pinecone · React Three Fiber**

[View Repository](https://github.com/Srijan-Petwal/R3F-Document-Helper-Agent)

</div>

---

## Overview

I built this project to explore how an LLM can work with **real documentation instead of relying only on its internal knowledge**.

The agent retrieves relevant React Three Fiber documentation from a Pinecone vector store and uses it as context while answering questions.

Rather than making retrieval a fixed step in every query, the retrieval system is exposed as a **tool to a LangGraph agent**.

```text
Documentation → Retrieval → Agent → Answer
```

---

## Demo

The repository contains a demo video:

**[▶ View Demo](./document-helper-agent-R3F-demo%20(1).webm)**

> If GitHub does not render the `.webm` inline, open the video file directly from the repository.

---

## Architecture

```text
        React Three Fiber Docs
                  │
                  ▼
           Tavily Crawl
                  │
                  ▼
        Document Processing
                  │
                  ▼
          Text Splitting
                  │
                  ▼
             Embeddings
                  │
                  ▼
             Pinecone
                  │
                  ▼
          ┌───────────────┐
          │   LangGraph   │
          │     Agent     │
          └───────┬───────┘
                  │
                  ▼
              Response
```

### Retrieval Flow

```text
User Question
      ↓
    Agent
      ↓
retrieve_context
      ↓
   Pinecone
      ↓
Relevant R3F Documentation
      ↓
    Agent
      ↓
   Answer
```

---

## Tech Stack

### Agent / LLM

- Python
- LangChain
- LangGraph
- OpenRouter
- LangSmith

### RAG

- Tavily Crawl
- Pinecone
- LangChain Documents
- RecursiveCharacterTextSplitter
- Embeddings

### Development

- uv
- python-dotenv

---

## Project Structure

```text
R3F-Document-Helper-Agent/
│
├── r3f-logo.png
├── document-helper-agent-R3F-demo (1).webm
├── README.md
├── .gitignore
├── .python-version
├── pyproject.toml
├── uv.lock
│
└── src/
    └── document_helper_rag_based_agent/
        ├── __init__.py
        ├── ingestion.py
        ├── logger.py
        ├── ui.py
        │
        └── backend/
            ├── __init__.py
            ├── core.py
            └── test.py
```

### Main Components

- **`ingestion.py`** — crawls, processes, chunks and embeds the documentation.
- **`backend/core.py`** — retrieval tool and agent workflow.
- **`ui.py`** — application interface.
- **`logger.py`** — logging utilities.

---

## How It Works

### 1. Documentation Ingestion

The R3F documentation is crawled using Tavily and converted into LangChain documents.

```text
R3F Documentation
        ↓
    Tavily Crawl
        ↓
LangChain Documents
        ↓
    Text Splitting
```

The documents are split into smaller chunks before embedding so retrieval can return focused pieces of documentation.

### 2. Embeddings & Vector Storage

The chunks are converted into embeddings and stored in **Pinecone**.

The embedding workflow uses OpenRouter through LangChain's embedding interface.

### 3. Agentic Retrieval

The Pinecone retriever is exposed to the agent through a retrieval tool:

```text
retrieve_context
```

The agent can use this tool when it needs relevant R3F documentation.

```text
Question
   ↓
 Agent
   ↓
Tool Call
   ↓
Pinecone Retrieval
   ↓
Documentation Context
   ↓
 Agent
   ↓
Answer
```

---

## Why R3F?

React Three Fiber sits at the intersection of **React and Three.js**, with its own abstractions and ecosystem.

When working with APIs such as:

- `Canvas`
- `useFrame`
- `useThree`
- Drei
- loaders
- materials
- scene objects
- physics integrations

having the actual documentation available to the model is useful.

That made R3F a good domain for experimenting with document-grounded agents.

---

## RAG → Agentic RAG

A conventional RAG pipeline looks like:

```text
Question
   ↓
Retrieve
   ↓
Context
   ↓
LLM
   ↓
Answer
```

This project experiments with:

```text
Question
   ↓
Agent
   ↓
Tool Call
   ↓
Retrieve Documentation
   ↓
Reason
   ↓
Answer
```

The retriever becomes a **capability available to the agent**, rather than a mandatory first step.

---

## Observability

The project uses **LangSmith** for tracing the workflow.

This helps inspect:

- Agent execution
- Tool calls
- Retrieval
- LLM calls
- Execution flow

For agentic systems, understanding *what the agent actually did* is almost as important as the final answer.

---

## Getting Started

### Prerequisites

You'll need:

- Python 3.13+
- uv
- Pinecone account
- OpenRouter API key
- Tavily API key
- LangSmith API key

### 1. Clone the Repository

```bash
git clone https://github.com/Srijan-Petwal/R3F-Document-Helper-Agent.git

cd R3F-Document-Helper-Agent
```

### 2. Install Dependencies

This project uses `uv` for dependency management.

```bash
uv sync
```

Activate the environment if required.

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

### 3. Environment Variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_key
TAVILY_API_KEY=your_key
PINECONE_API_KEY=your_key

LANGSMITH_API_KEY=your_key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=R3F-Document-Helper-Agent
```

Keep `.env` local and **never commit it**.

### 4. Run

Run the ingestion pipeline first to populate Pinecone with the documentation.

Then start the application through the configured project entry point.

---

## What I Learned

This project was mainly about understanding the pieces underneath a RAG agent:

- Crawling real documentation
- Document processing and chunking
- Embeddings and vector search
- Pinecone retrieval
- Tool-based retrieval
- LangGraph agent workflows
- OpenRouter integration
- LangSmith tracing
- Debugging agent execution
- Managing the project with `uv`

The goal wasn't just to make another chatbot.

It was to understand what happens when you give an LLM **external knowledge, retrieval and tools**, and let it decide how to use them.

---

## Current Status

The core retrieval pipeline and UI are implemented.

```text
Documentation
      ↓
  Ingestion
      ↓
   Pinecone
      ↓
  Retrieval
      ↓
    Agent
      ↓
   Answer
```

Possible next steps include better retrieval evaluation, reranking, source attribution, memory and improved agent routing.

---

## Future Improvements

- Better retrieval evaluation
- Reranking
- Hybrid retrieval
- Source attribution
- Conversation memory
- Streaming responses
- Automated RAG evaluation
- Documentation versioning
- Improved agent routing

---

## Repository

<div align="center">

### [View R3F Document Helper Agent on GitHub →](https://github.com/Srijan-Petwal/R3F-Document-Helper-Agent)

</div>

---

## A Note

I tend to learn these systems by actually building them rather than trying to understand every abstraction beforehand.

This project was one of those experiments.

The interesting part wasn't just getting a model to answer a question. It was understanding what happens when you give an LLM **external knowledge, retrieval and tools**, and then start debugging what it actually does.

That's where the gap between *"I know what RAG is"* and *"I can build and debug a RAG system"* becomes pretty obvious.