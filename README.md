<div align="center">

<img src="https://img.shields.io/badge/FloatChat-Brain%20%7C%20AI%20Core-0ea5e9?style=for-the-badge&logo=openai&logoColor=white" alt="FloatChat Brain"/>

# 🧠 FloatChat — AI Brain (Orchestration Layer)

**The intelligent core of FloatChat — an AI-powered conversational platform for querying and exploring ARGO oceanographic float data in real time.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![LangChain](https://img.shields.io/badge/LangChain-ReAct%20Agent-1C3C3C?style=flat-square&logo=langchain&logoColor=white)](https://langchain.com/)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector%20DB-00BFA6?style=flat-square&logo=pinecone&logoColor=white)](https://www.pinecone.io/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

**[🌐 Frontend (Landing Page & Chat UI)](https://github.com/Hiten1007/float-landing-page)** &nbsp;|&nbsp;
**[⚙️ Backend (API & Database Layer)](https://github.com/Hiten1007/FloatChat-Backend)**

---

</div>

## 📖 Table of Contents

- [About the Project](#-about-the-project)
- [The Full System Architecture](#-the-full-system-architecture)
- [Repository Overview — What This Repo Does](#-repository-overview--what-this-repo-does)
- [Connected Repositories](#-connected-repositories)
  - [Frontend Repo](#-frontend--float-landing-page)
  - [Backend Repo](#-backend--floatchat-backend)
- [Tech Stack](#-tech-stack)
- [How the AI Agent Works](#-how-the-ai-agent-works)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [Data Pipeline — Embedding ARGO Data](#-data-pipeline--embedding-argo-data)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)

---

## 🌊 About the Project

**FloatChat** is an end-to-end conversational AI system built for **SIH 2025 (Smart India Hackathon)** that allows scientists, researchers, and enthusiasts to query real-world **ARGO oceanographic float data** using natural language.

> ARGO floats are autonomous underwater robots deployed globally to measure ocean temperature, salinity, pressure, dissolved oxygen, and more. FloatChat makes this data conversationally accessible.

Instead of writing complex SQL or remembering data schemas, a user can simply ask:

> *"What was the average temperature recorded by platform 2900765 last month?"*
> *"How does an ARGO float transmit data?"*
> *"Which float recorded the highest salinity ever?"*

The AI takes over — it decides what tools to use, queries the right database, and returns a clean, structured answer.

---

## 🏗 The Full System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         USER (Browser)                               │
│              Interacts via the React / Next.js UI                    │
└───────────────────────────┬──────────────────────────────────────────┘
                            │  HTTP
                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│          🌐 FRONTEND REPO — float-landing-page                       │
│  Landing page, Chat UI, renders answer_blocks (text + tables)        │
│  https://github.com/Hiten1007/float-landing-page                     │
└───────────────────────────┬──────────────────────────────────────────┘
                            │  POST /api/llm/query
                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│  🧠 THIS REPO — FloatChat-Brain (AI Orchestration / Python Flask)    │
│                                                                      │
│   ┌──────────────────────────────────────────────────┐              │
│   │            LangChain ReAct Agent                 │              │
│   │   (Decides which tool to call, in what order)    │              │
│   └────────────────┬─────────────────────────────────┘              │
│                    │                                                 │
│        ┌───────────┴───────────┐                                    │
│        ▼                       ▼                                    │
│  SQL_Database_Tool       Vector_Database_Tool                       │
│  (Quantitative queries)  (Semantic / RAG queries)                   │
│        │                       │                                    │
│        │                       └──► Pinecone Vector DB              │
│        │                            (ARGO metadata embeddings)      │
│        │                                                            │
│        └──► POST /api/getsqldata                                    │
│                    │                                                 │
└────────────────────┼─────────────────────────────────────────────────┘
                     │  HTTP (internal)
                     ▼
┌──────────────────────────────────────────────────────────────────────┐
│  ⚙️ BACKEND REPO — FloatChat-Backend (TypeScript / Node.js)         │
│  Handles SQL queries against the PostgreSQL ARGO float database      │
│  https://github.com/Hiten1007/FloatChat-Backend                     │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Repository Overview — What This Repo Does

This is the **AI Brain** of the FloatChat ecosystem. It is a **Python Flask server** that hosts a **LangChain ReAct Agent** capable of intelligently orchestrating two tools — a SQL query tool and a semantic vector search tool — to answer complex, natural language questions about ARGO oceanographic float data.

### Core Responsibilities

| Responsibility | Description |
|---|---|
| **Agent Orchestration** | Runs a LangChain `create_react_agent` with a custom system prompt that decides *which* tool to use based on the query type |
| **SQL Tool** | Wraps calls to the TypeScript backend API (`/api/getsqldata`), accepting a structured JSON query and returning measurement data |
| **Vector / RAG Tool** | Embeds the user query using `all-MiniLM-L6-v2`, retrieves semantically similar ARGO documents from Pinecone, and synthesizes an answer using LangChain QA |
| **Response Formatting** | Parses the agent's raw output and extracts a structured `answer_blocks` JSON (text blocks + table blocks) for clean rendering on the frontend |
| **Data Ingestion** | `embed.py` batch-processes the ARGO metadata CSV, generates vector embeddings, and upserts them into the Pinecone index |

---

## 🔗 Connected Repositories

### 🌐 Frontend — [float-landing-page](https://github.com/Hiten1007/float-landing-page)

**What it does:**

The frontend is the face of FloatChat. It provides:

- A **landing page** introducing the FloatChat platform, showcasing the ARGO float mission and the power of AI-driven ocean data exploration.
- An interactive **Chat UI** where users type natural language questions and receive AI-generated responses.
- **Dynamic rendering** of structured `answer_blocks` returned by this Brain server — text explanations and data tables are displayed cleanly in the chat interface.
- Handles **conversation history** to maintain multi-turn dialogue context.

**Tech Stack:** React / Next.js, TypeScript, Tailwind CSS

**Connects to:** This Brain repo via `POST /api/llm/query`

---

### ⚙️ Backend — [FloatChat-Backend](https://github.com/Hiten1007/FloatChat-Backend)

**What it does:**

The backend is the **data engine** for all structured, quantitative ARGO measurements. It:

- Hosts a **TypeScript / Node.js REST API** that receives structured query payloads (JSON) from the Brain's SQL tool.
- Executes **flexible SQL queries** against a **PostgreSQL database** containing millions of ARGO float measurements — supporting `find`, `aggregate`, `count`, and `groupBy` operations with filters, ordering, and pagination.
- Stores real ARGO sensor data: `platform_code`, `date_time`, `latitude`, `longitude`, `pres_adjusted`, `temp_adjusted`, `psal_adjusted`, `dox2_adjusted`, `cphl_adjusted`, `bbp700_adjusted`, `fluo_adjusted`.
- Returns clean JSON results back to the Brain, which the agent uses to formulate its final answer.

**Tech Stack:** TypeScript, Node.js, Express, PostgreSQL

**Connects to:** This Brain repo — is called internally by the `SQL_Database_Tool` at `http://localhost:3000/api/getsqldata`

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **Web Framework** | Flask 3.x |
| **AI Agent** | LangChain ReAct Agent (`create_react_agent`) |
| **LLM** | Configurable via `app/brain/llm.py` (Gemini / OpenAI compatible) |
| **Vector Database** | Pinecone (`argo-floats-india` index) |
| **Embedding Model** | `sentence-transformers/all-MiniLM-L6-v2` (384-dim, CPU-friendly) |
| **Schema Validation** | Pydantic v2 |
| **SQL Proxy** | Internal HTTP call to the TypeScript backend |
| **Data Processing** | Pandas, psycopg2 |
| **Prompt Engineering** | Custom ReAct system prompt with domain-specific tool selection rules |

---

## 🤖 How the AI Agent Works

The Brain uses a **LangChain ReAct (Reason + Act) Agent**, which follows a structured thought loop:

```
User Query
    │
    ▼
Thought: Analyze the question — is it quantitative or qualitative?
    │
    ├── Quantitative (numbers, measurements, filters)
    │       └── Action: SQL_Database_Tool
    │                   └── Calls TypeScript Backend API
    │
    └── Qualitative (explanations, definitions, context)
            └── Action: Vector_Database_Tool
                        └── Embeds query → Pinecone search → LangChain QA
    │
    ▼
Observation: Parse tool result
    │
    ▼
Repeat if needed (multi-step reasoning)
    │
    ▼
Final Answer: Structured JSON { "answer_blocks": [...] }
```

### Tool Selection Logic (from System Prompt)

| Query Type | Tool Used |
|---|---|
| *"What is the temperature for platform X?"* | `SQL_Database_Tool` |
| *"How many floats were deployed?"* | `SQL_Database_Tool` |
| *"How does an ARGO float work?"* | `Vector_Database_Tool` |
| *"What is the mission of project INDIA-ARGO?"* | `Vector_Database_Tool` |
| *"Average salinity for last month near coordinates X,Y"* | `SQL_Database_Tool` |

### Response Format

All responses are structured as:

```json
{
  "agent_thought_process": [...],
  "final_answer": {
    "status": "success",
    "message": "Response processed successfully.",
    "answer_blocks": [
      {
        "type": "text",
        "content": { "message": "The average temperature was 25.3°C." }
      },
      {
        "type": "table",
        "content": {
          "headers": ["Date", "Temperature (°C)", "Salinity (PSU)"],
          "rows": [["2025-09-11T14:00:00Z", 28.1, 34.5]]
        }
      }
    ]
  }
}
```

---

## 📁 Project Structure

```
FloatChat-Brain/
│
├── run.py                         # Entry point — starts the Flask server on port 5000
├── embed.py                       # One-time data pipeline: CSV → embeddings → Pinecone
├── cleaned_metadata[1].csv        # Raw ARGO float metadata (40 fields, 75k+ records)
│
└── app/
    ├── __init__.py                # Flask app factory — registers blueprints, inits services
    ├── config.py                  # Loads .env into Flask app.config
    │
    ├── brain/
    │   ├── llm.py                 # LLM instance (Gemini / OpenAI)
    │   └── agent_prompts.py       # Full ReAct system prompt with tool rules & output format
    │
    ├── controllers/
    │   ├── llm_controller.py      # Agent executor, tool wrappers, response parser
    │   └── data_controller.py     # Handles CSV/NetCDF insert requests
    │
    ├── services/
    │   ├── sqldb_service.py       # HTTP proxy to TypeScript backend + PostgreSQL uploader
    │   └── vector_service.py      # Pinecone init, SentenceTransformer embedding, RAG QA
    │
    ├── routes/
    │   ├── llm_routes.py          # POST /api/llm/query — main chat endpoint
    │   └── data_routes.py         # POST /api/data/insert — data ingestion endpoint
    │
    └── schemas/
        ├── sql_schema.py          # Pydantic models: QueryInput, FilterField, AggregateField
        └── vector_schema.py       # Pydantic model: VectorQueryInput
```

---

## 🔌 API Endpoints

### `POST /api/llm/query`

The primary endpoint. Accepts a natural language query and returns a structured AI response.

**Request:**
```json
{
  "query": "What was the average salinity recorded by platform 2900765?"
}
```

**Response:**
```json
{
  "agent_thought_process": [ ... ],
  "final_answer": {
    "status": "success",
    "message": "Response processed successfully.",
    "answer_blocks": [
      {
        "type": "text",
        "content": { "message": "The average salinity for platform 2900765 is 34.7 PSU." }
      }
    ]
  }
}
```

---

### `POST /api/data/insert`

Internal endpoint for inserting processed ARGO NetCDF data into the PostgreSQL database via the backend.

---

## 📊 Data Pipeline — Embedding ARGO Data

`embed.py` is the one-time ingestion script that populates the Pinecone vector database:

1. **Reads** the `cleaned_metadata[1].csv` file containing 40 ARGO metadata fields (platform number, project name, PI name, cycle number, data centre, calibration history, etc.)
2. **Converts** each row into a descriptive text block using a fixed field order
3. **Embeds** each text using `all-MiniLM-L6-v2` (384-dimensional vectors, fast on CPU)
4. **Upserts** each vector + metadata into the `argo-floats-india` Pinecone index
5. **Supports resuming** from a specific row index (`i <= 75105: continue`)

This powers the `Vector_Database_Tool`'s semantic search capability.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A running instance of the **[FloatChat-Backend](https://github.com/Hiten1007/FloatChat-Backend)** (TypeScript server on `localhost:3000`)
- A **Pinecone** account with an index named `argo-floats-india`
- Your LLM API key (Gemini / OpenAI)

### Installation

```bash
# 1. Clone this repository
git clone https://github.com/Hiten1007/FloatChat-Brain.git
cd FloatChat-Brain

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Fill in your API keys (see Environment Variables section below)

# 5. (First time only) Run the embedding pipeline to populate Pinecone
python embed.py

# 6. Start the Flask server
python run.py
```

The server starts at `http://localhost:5000`.

---

## 🔑 Environment Variables

Create a `.env` file in the root directory:

```env
# LLM Provider
GOOGLE_API_KEY=your_google_gemini_api_key
# OR
OPENAI_API_KEY=your_openai_api_key

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key

# (Optional) PostgreSQL — only needed if using the direct DB uploader
DATABASE_URL=postgresql://user:password@localhost:5432/floatchat_db
```

---

<div align="center">

Built with ❤️ for **Smart India Hackathon 2025**

**[🌐 Frontend Repo](https://github.com/Hiten1007/float-landing-page)** &nbsp;|&nbsp; **[⚙️ Backend Repo](https://github.com/Hiten1007/FloatChat-Backend)**

</div>
