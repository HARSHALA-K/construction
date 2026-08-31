# 🏗️ Construction AI Assistant

> An AI-powered construction assistant combining Retrieval-Augmented Generation (RAG), vector search, web retrieval, deterministic construction calculators, MCP-based tools, and agent orchestration.

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-red)](https://qdrant.tech/)
[![RAG](https://img.shields.io/badge/AI-RAG-purple)](#architecture)
[![MCP](https://img.shields.io/badge/Tools-MCP-orange)](#mcp-tool-integration)

---

## 📌 Overview

The Construction AI Assistant is a domain-focused AI system designed to answer construction-related questions using a combination of:

* Company/domain knowledge stored in a vector database
* Retrieval-Augmented Generation (RAG)
* Semantic embeddings
* Current information retrieved from the web
* Deterministic construction calculators
* MCP-based tool integration
* AI agent orchestration
* FastAPI backend services
* Streamlit user interface

The main design principle is to separate responsibilities:

> **RAG retrieves knowledge, tools perform deterministic calculations, web search provides current information, and the LLM handles reasoning and explanation.**

---

## 🎯 Problem

Construction information is often distributed across:

* Technical documents
* Material specifications
* Safety documentation
* Project information
* Internal knowledge
* Pricing information
* Calculation spreadsheets
* External websites

Searching through these sources manually can be time-consuming.

The goal of this project is to provide a natural-language interface where users can ask construction questions and receive answers grounded in available information and supported by deterministic tools where appropriate.

---

## ✨ Key Features

### 🔎 Retrieval-Augmented Generation

Construction documents are processed into chunks, converted into embeddings, and stored in Qdrant.

For a user query:

```text
User Question
      ↓
Embedding
      ↓
Qdrant Semantic Search
      ↓
Relevant Construction Chunks
      ↓
LLM
      ↓
Grounded Response
```

---

### 🌐 Web Search

Some construction information changes over time.

For example:

* Material prices
* Current market information
* External references
* Updated information

The system can retrieve relevant web information when required instead of relying exclusively on the static knowledge base.

---

### 🧮 Deterministic Construction Calculators

The system includes construction-specific calculators such as:

* Tile estimation
* Material estimation
* Brickwork estimation
* Project cost estimation
* Interior cost estimation

The calculation logic is implemented as deterministic Python functions.

This is intentional.

The LLM is responsible for understanding the request and explaining the result, while the calculator performs the numerical computation.

---

### 🔌 MCP Tool Integration

The calculation capabilities can be exposed as tools through MCP.

This allows an AI agent to invoke a calculation when required.

For example:

```text
User:
"How many tiles do I need for a 10 × 12 ft room
using 600 × 600 mm tiles?"

        ↓

Agent understands the request

        ↓

MCP tile calculation tool

        ↓

Deterministic calculation

        ↓

Result returned to agent

        ↓

LLM explains result
```

The Streamlit Calculator page and MCP tools serve different purposes:

* **Calculator UI:** direct human interaction
* **MCP tools:** AI/agent-accessible capabilities

---

### 🤖 Agent Exploration

The project includes experimental integrations with:

* CrewAI
* AutoGen

These were explored to understand agent orchestration, tool usage, and multi-step construction workflows.

The agent layer is intentionally separated from the core RAG and calculator components so that different orchestration approaches can be evaluated without redesigning the underlying system.

---

### 🚀 FastAPI Backend

FastAPI provides a backend/API layer between the application interface and the underlying AI components.

This keeps the architecture modular and allows the frontend to be replaced independently in the future.

---

### 🖥️ Streamlit Interface

The Streamlit application provides interfaces for:

* Construction chat
* Calculators
* Agent experimentation
* Feedback
* Project information

The interface is primarily intended for prototyping and demonstration.

---

# 🏛️ Architecture

```text
                         ┌──────────────────┐
                         │      User        │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    Streamlit     │
                         │    Interface     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  FastAPI / App   │
                         │     Backend      │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
       ┌─────────────┐     ┌─────────────┐    ┌─────────────┐
       │    RAG      │     │   MCP Tools │    │ Web Search  │
       └──────┬──────┘     └──────┬──────┘    └──────┬──────┘
              │                   │                   │
              ▼                   ▼                   │
       ┌─────────────┐     ┌─────────────┐            │
       │   Qdrant    │     │Deterministic│            │
       │ Vector DB   │     │ Calculators │            │
       └──────┬──────┘     └─────────────┘            │
              │                                       │
              └───────────────────┬───────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │       LLM        │
                         │ Reasoning / Gen. │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Final Response + │
                         │     Sources      │
                         └──────────────────┘
```

---

# 🔄 RAG Pipeline

```text
Construction Documents
        ↓
Document Processing
        ↓
Chunking
        ↓
Embedding Model
        ↓
Qdrant
        ↓
Semantic Retrieval
        ↓
Relevant Context
        ↓
LLM
        ↓
Grounded Answer
```

The project experimented with different chunking approaches, including recursive, semantic, and sliding-window strategies.

A lightweight Sentence Transformers model such as `all-MiniLM-L6-v2` was used as an embedding baseline.

---

# 🧠 Intent-Based Routing

The application identifies different types of construction requests and routes them accordingly.

Example:

```text
User Question
     │
     ▼
Intent Detection
     │
 ┌───┼────────┬──────────┐
 ▼   ▼        ▼          ▼
Tile Material Project   Interior
 │     │        │          │
 ▼     ▼        ▼          ▼
Tool  Tool     Tool       Tool
```

Questions that do not match a calculator intent can proceed through the RAG + web retrieval pipeline.

---

# 🧮 Example

### Input

```text
How many bricks are required for a wall
of length 20 m, width 10 m and thickness 0.15 m?
```

The system extracts the relevant parameters and routes the request to the material calculation capability.

The result depends on assumptions such as:

* Brick dimensions
* Mortar joint
* Wall dimensions
* Openings
* Wastage

The system is therefore designed to present estimates together with relevant assumptions rather than treating a construction estimate as an absolute value.

---

# 🌐 Internal Knowledge + Web Knowledge

One of the project's important capabilities is combining different information sources.

For example:

```text
Stable construction information
          ↓
      Qdrant / RAG

Current information
          ↓
      Web Search

Numerical calculation
          ↓
   Deterministic Tool

          ↓
        LLM

          ↓
    Final Response
```

This allows the system to distinguish between information that can come from a controlled knowledge base and information that may require current retrieval.

---

# 🤖 Agent Framework Exploration

The project includes separate experiments with CrewAI and AutoGen.

The purpose was to investigate:

* Agent orchestration
* Tool calling
* Multi-step reasoning
* Construction-specific workflows
* Framework differences
* Integration with existing application capabilities

The project does not assume that an agent framework is required for every query.

Simple retrieval or calculation tasks can be handled through simpler deterministic pipelines.

---

# 🛠️ Technology Stack

| Component        | Technology            |
| ---------------- | --------------------- |
| Language         | Python                |
| Frontend         | Streamlit             |
| API              | FastAPI               |
| LLM              | Groq-hosted LLM       |
| RAG              | Custom RAG pipeline   |
| Vector Database  | Qdrant                |
| Embeddings       | Sentence Transformers |
| Web Retrieval    | Web search            |
| Tool Interface   | MCP                   |
| Agent Frameworks | CrewAI, AutoGen       |
| Data Processing  | Pandas                |
| Logging          | Python Logging        |

---

# 📂 Project Structure

```text
construction/
│
├── backend/
│   ├── agents/
│   ├── calculators/
│   ├── embedding/
│   ├── intent_detector/
│   ├── llm/
│   ├── qdrant/
│   ├── rag/
│   ├── router/
│   └── utils/
│
├── mcp_client/
├── mcp_server/
├── assets/
├── data/
├── tests/
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

> The exact structure may differ depending on the current version of the repository.

---

# 🚀 Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

## 2. Create a virtual environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create a `.env` file based on `.env.example`.

Example:

```env
GROQ_API_KEY=your_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
```

Never commit real API keys or credentials.

## 5. Run the Streamlit application

```bash
streamlit run app.py
```

---

# 🧪 Testing

The project was tested using several construction scenarios including:

* Material estimation
* Brickwork estimation
* Tile estimation
* Construction cost estimation
* Construction knowledge retrieval
* High-rise construction questions
* Web + internal knowledge retrieval
* Agent-based construction questions

Testing also exposed practical limitations such as LLM provider rate limits and the need for stronger systematic evaluation.

---

# ⚠️ Current Limitations

This project is currently a functional prototype rather than a production construction decision system.

Important limitations include:

* Construction estimates depend on assumptions and should be validated against project-specific requirements.
* Web sources require quality and relevance validation.
* Agent workflows can increase latency and token consumption.
* Production deployment would require stronger authentication and authorization.
* A larger evaluation benchmark is required to quantitatively measure retrieval and answer quality.
* Critical engineering decisions should be reviewed by qualified professionals.

---

# 🔮 Future Improvements

Potential next steps include:

### AI / Retrieval

* Evaluate stronger embedding models such as BGE and E5
* Add reranking
* Improve retrieval evaluation
* Add automated RAG evaluation
* Improve source attribution

### Tools

* Expand construction calculators
* Add BOQ analysis
* Add material price databases
* Add vendor lookup
* Add project estimation workflows

### Production

* Authentication and role-based access
* Document-level permissions
* Monitoring and observability
* Usage and cost tracking
* Better error handling
* Scalable deployment

### Agent Systems

* Compare CrewAI and AutoGen systematically
* Evaluate tool-selection accuracy
* Add multi-step construction workflows
* Measure agent latency and token consumption

---

# 📊 Evaluation Roadmap

Rather than evaluating the system only through demonstrations, a production version should be evaluated using a benchmark of real construction questions.

Important metrics include:

| Area           | Example Metric             |
| -------------- | -------------------------- |
| Retrieval      | Recall@K / Precision@K     |
| Answer Quality | Groundedness / Correctness |
| Tool Usage     | Correct tool selection     |
| Calculations   | Numerical accuracy         |
| Latency        | Response time              |
| LLM Cost       | Tokens / request           |
| Reliability    | Error / failure rate       |

---

# 💡 Design Philosophy

The project follows a simple principle:

> **Use AI where reasoning is useful and deterministic software where exact computation is required.**

The LLM should not be responsible for every task.

Instead:

* Retrieval handles knowledge access.
* Vector search handles semantic matching.
* Web search handles current external information.
* Deterministic tools handle calculations.
* MCP provides a standardized tool interface.
* Agents coordinate multi-step tasks.
* The LLM handles reasoning and natural-language interaction.

---

# 📸 Demo

Add screenshots or a short GIF here:

```text
docs/
├── chat-demo.png
├── calculator-demo.png
├── agents-demo.png
└── architecture.png
```

A short screen recording demonstrating:

1. A RAG question
2. A calculation request
3. A web-search question
4. An MCP/agent tool call

is recommended.

---

# 🎓 Project Context

This project was developed as an applied AI / RAG exploration focused on construction-domain use cases.

It demonstrates the integration of:

**RAG + Vector Search + Web Retrieval + Deterministic Tools + MCP + Agents + FastAPI + Streamlit**

rather than treating an LLM as a standalone chatbot.

---

# 📜 Disclaimer

This project is intended for educational, prototyping, and AI engineering demonstration purposes.

Construction calculations and recommendations should be independently verified against applicable engineering standards, project specifications, and qualified professional advice before being used for real-world construction decisions.

---

## 👩‍💻 Author

**Harshala Koli**

BSc Artificial Intelligence

Interested in:

* Applied AI
* AI Engineering
* RAG Systems
* AI Agents
* LLM Applications
* Machine Learning
* Backend AI Systems
