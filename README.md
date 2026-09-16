# R3F Doc Helper Agent

<p align="center">
  <img src="src/document_helper_rag_based_agent/r3f-logo.png" alt="React Three Fiber" width="180"/>
</p>

<p align="center">
  <b>A RAG-based document helper agent for navigating and understanding React Three Fiber documentation.</b>
</p>

<p align="center">
  Retrieval • Agents • RAG • React Three Fiber • LangGraph • Pinecone
</p>

---

## What is this?

I built **R3F Doc Helper Agent** as a practical experiment in combining **Retrieval-Augmented Generation with an agentic workflow**.

The idea is simple:

> Instead of asking an LLM to answer questions about React Three Fiber from whatever knowledge it already has, give it access to the actual documentation and let it retrieve the relevant context before answering.

The system crawls the relevant documentation, processes and embeds the content, stores it in a vector database, and exposes retrieval as a tool that the agent can use when answering questions.

This started as a document/RAG project, but the goal was to move beyond a simple `query → retrieve → answer` pipeline and explore how an **agent can decide when it needs external context**.

---

## Demo

The repository contains a demo of the application:

**`document-helper-agent-R3F-demo (1).webm`**

The video is kept in the root directory of the repository.

---

## Architecture

At a high level, the project is divided into two stages:

```text
                    ┌─────────────────────┐
                    │  React Three Fiber  │
                    │   Documentation     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Tavily Crawl     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ LangChain Documents │
                    │ + URL Metadata      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Text Splitting      │
                    │ RecursiveCharacter  │
                    │ TextSplitter        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Embeddings      │
                    │     OpenRouter      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Pinecone       │
                    │    Vector Store     │
                    └──────────┬──────────┘
                               │
                               │ retrieve_context
                               ▼
                    ┌─────────────────────┐
                    │     LangGraph       │
                    │       Agent         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Response       │
                    └─────────────────────┘
```

---

## How it works

### 1. Documentation ingestion

The documentation is crawled using **Tavily Crawl**.

The crawled pages are converted into LangChain `Document` objects while retaining useful metadata such as the source URL.

```text
Documentation
      ↓
Tavily Crawl
      ↓
LangChain Documents
      ↓
Recursive Character Text Splitter
      ↓
Embeddings
      ↓
Pinecone
```

The text is split into smaller chunks before embedding so that retrieval can return focused pieces of documentation instead of entire pages.

---

### 2. Embeddings and vector storage

The chunks are converted into vector representations and stored in **Pinecone**.

The embedding workflow uses OpenRouter through LangChain's `OpenAIEmbeddings` interface with:

```text
nvidia/nemotron-3-embed-1b:free
```

The ingestion pipeline also batches embedding requests to make the process more manageable.

---

### 3. Agentic retrieval

The interesting part of the project is the retrieval layer.

Instead of hardcoding retrieval as the first step for every query, the Pinecone retriever is exposed to the agent through a retrieval tool:

```text
retrieve_context
```

The agent is implemented using **LangGraph/LangChain**.

Conceptually:

```text
User Question
      ↓
    Agent
      │
      ├── Does it need documentation?
      │
      └── retrieve_context
                ↓
             Pinecone
                ↓
        Relevant R3F Context
                ↓
             Agent
                ↓
             Answer
```

This allows the project to explore a more flexible workflow than a traditional fixed RAG chain.

---

## Tech Stack

### AI / Agentic

* **LangChain** — LLM and retrieval ecosystem
* **LangGraph** — agent workflow/orchestration
* **OpenRouter** — model and embedding access
* **LangSmith** — tracing and observability

### Retrieval / Data

* **Tavily Crawl** — documentation ingestion
* **Pinecone** — vector database
* **RecursiveCharacterTextSplitter** — document chunking
* **LangChain Document** — document representation and metadata

### Development

* **Python 3.13.5**
* **uv** — Python project and dependency management
* **python-dotenv** — environment configuration

---

## Project Structure

```text
document-helper-rag-based-agent/
│
├── document-helper-agent-R3F-demo (1).webm
├── README.md
├── .gitignore
├── .python-version
├── pyproject.toml
├── uv.lock
│
└── src/
    └── document_helper_rag_based_agent/
        │
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

### Important files

**`ingestion.py`**

Handles the documentation ingestion pipeline:

```text
Tavily → Documents → Chunking → Embeddings → Pinecone
```

**`backend/core.py`**

Contains the retrieval/agent backend, including the Pinecone retrieval tool and LangGraph/LangChain agent workflow.

**`ui.py`**

Contains the user interface for interacting with the document helper.

**`logger.py`**

Handles project logging.

---

## Getting Started

### Prerequisites

You'll need:

* Python 3.13+
* `uv`
* A Pinecone account
* An OpenRouter API key
* A Tavily API key
* A LangSmith API key if tracing is enabled

---

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/document-helper-rag-based-agent.git

cd document-helper-rag-based-agent
```

---

### 2. Create the environment

This project uses **uv** for dependency and environment management.

```bash
uv sync
```

Activate the environment if required:

**Windows**

```bash
.venv\Scripts\activate
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

---

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_key
TAVILY_API_KEY=your_key
PINECONE_API_KEY=your_key

LANGSMITH_API_KEY=your_key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=document-helper-rag-based-agent
```

**Do not commit `.env`.**

The repository should only contain a safe `.env.example` file if environment-variable documentation is needed.

---

## Running the project

Run the ingestion pipeline first so that the documentation is crawled, embedded, and stored in Pinecone.

Then start the application/UI using the project's entry point.

The exact command depends on the configured project entry point in `pyproject.toml`.

---

## Why R3F?

React Three Fiber is a good example of a domain where documentation matters.

The ecosystem involves concepts from both **React and Three.js**, along with abstractions introduced by R3F and its surrounding libraries.

When working with things like:

* `Canvas`
* `useFrame`
* `useThree`
* Drei
* Three.js objects
* loaders
* materials
* scene graphs
* rendering
* physics integrations

the difference between a plausible answer and an answer grounded in the actual documentation can be significant.

That made R3F a useful domain for experimenting with document-grounded agents.

---

## RAG vs Agentic RAG

A traditional RAG pipeline generally looks like:

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

This project explores:

```text
Question
   ↓
Agent
   ↓
Decide / use tool
   ↓
Retrieve documentation
   ↓
Reason over context
   ↓
Answer
```

The distinction is small at the surface but interesting from an engineering perspective.

The retrieval system becomes a **capability available to the agent**, rather than simply a mandatory preprocessing step.

---

## Observability

The project uses **LangSmith** for tracing the agent workflow.

This makes it possible to inspect things such as:

* Agent execution
* Tool calls
* Retrieval steps
* LLM calls
* Execution flow
* Debugging information

For agentic systems, being able to see *what the system actually did* is almost as important as seeing the final answer.

---

## What I explored while building this

This project was less about building another chatbot and more about understanding the pieces underneath one.

Some of the things I worked through were:

* Crawling real documentation instead of relying on static datasets
* Converting web content into structured documents
* Chunking documentation for retrieval
* Embedding and indexing documents
* Building a Pinecone retrieval layer
* Exposing retrieval as an agent tool
* Building the workflow with LangGraph
* Connecting LangChain components through OpenRouter
* Tracing agent execution with LangSmith
* Debugging tool-bound model execution
* Managing the project with `uv`

There were also a few places where the theory and the actual implementation behaved differently than expected — which, honestly, was part of the point of building it.

---

## Current Status

The core retrieval pipeline and basic UI are implemented.

The current version focuses on the fundamental loop:

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

There is still plenty of room to improve the agent's reasoning, retrieval quality, evaluation, and overall product experience.

---

## Future Improvements

Some directions I want to explore:

* Better retrieval evaluation
* Hybrid / reranked retrieval
* More robust source attribution
* Improved agent/tool routing
* Conversation memory
* Streaming responses
* Automated RAG evaluation
* Better handling of documentation versions
* More detailed LangSmith evaluation
* Expanding beyond R3F documentation

---

## A small note on the project

I tend to learn these systems by actually building them rather than trying to understand every abstraction beforehand.

This project was one of those experiments.

The interesting part wasn't just getting a model to answer a question. It was understanding what happens when you give an LLM **tools, external knowledge, retrieval, and an execution graph**, and then start debugging what it actually does.

That's where the gap between *"I know what RAG is"* and *"I can build and debug a RAG system"* becomes pretty obvious.

---

## License

This project is intended primarily as a learning and experimentation project.
