<div align="center">

# 🌊 FloatChat — AI-Powered Ocean Data Platform

**Conversational AI for real-world ARGO oceanographic float data — built for Smart India Hackathon 2025.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://reactjs.org/)
[![LangChain](https://img.shields.io/badge/LangChain-ReAct%20Agent-1C3C3C?style=flat-square)](https://langchain.com/)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector%20DB-00BFA6?style=flat-square)](https://www.pinecone.io/)
[![Prisma](https://img.shields.io/badge/Prisma-ORM-2D3748?style=flat-square&logo=prisma&logoColor=white)](https://www.prisma.io/)

---

**[⚙️ FloatChat-Backend](https://github.com/Hiten1007/FloatChat-Backend)** &nbsp;·&nbsp;
**[🌐 float-landing-page (Frontend)](https://github.com/Hiten1007/float-landing-page)**

</div>

---

## 📖 Table of Contents

- [What is FloatChat?](#-what-is-floatchat)
- [System Architecture](#-system-architecture)
- [Repository Map](#-repository-map)
- [🧠 This Repo — FloatChat-Brain (AI Orchestration)](#-this-repo--floatchat-brain-ai-orchestration)
- [⚙️ FloatChat-Backend (TypeScript API + Database)](#%EF%B8%8F-floatchat-backend-typescript-api--database)
- [🌐 float-landing-page (React Frontend)](#-float-landing-page-react-frontend)
- [End-to-End Data Flow](#-end-to-end-data-flow)
- [Complete Tech Stack](#-complete-tech-stack)
- [Getting Started — Run the Full System](#-getting-started--run-the-full-system)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)

---

## 🌊 What is FloatChat?

FloatChat lets scientists, researchers, and ocean enthusiasts **query real ARGO float data using plain English**. Instead of writing SQL or remembering schema names, users can just ask:

> *"What was the average salinity near platform 2900765 last month?"*
> *"How does an ARGO float work?"*
> *"Which float recorded the highest temperature ever?"*

The AI reasons over two databases — a **PostgreSQL structured database** for measurements and a **Pinecone vector database** for documentation — and returns structured, beautifully rendered answers.

FloatChat is a **three-service system**:

| Service | Repo | Role |
|---|---|---|
| 🧠 **Brain** | This repo | LangChain ReAct agent, tool orchestration, RAG pipeline |
| ⚙️ **Backend** | [FloatChat-Backend](https://github.com/Hiten1007/FloatChat-Backend) | TypeScript/Express API, Prisma ORM, PostgreSQL |
| 🌐 **Frontend** | [float-landing-page](https://github.com/Hiten1007/float-landing-page) | React/Vite SPA, 3D ocean UI, Chat interface |

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER (Browser)                               │
│         React SPA — Landing Page, Chat UI, Map Dashboard        │
└──────────────────────────┬──────────────────────────────────────┘
                           │  POST http://localhost:3000/api/query
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  ⚙️  FloatChat-Backend  (TypeScript · Express · Port 3000)      │
│                                                                 │
│   POST /api/query      ──► forwards to Brain at :5000          │
│   POST /api/getsqldata ──► Prisma ORM ──► PostgreSQL           │
│   POST /insertdata/insert ──► forwards file to Brain           │
└───────┬──────────────────────────┬──────────────────────────────┘
        │ internal HTTP            │ internal HTTP
        ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  🧠  FloatChat-Brain   (Python · Flask · Port 5000)             │
│                                                                 │
│   ┌─────────────────────────────────────────┐                  │
│   │       LangChain ReAct Agent             │                  │
│   │  (Reasons → picks tool → acts → loops) │                  │
│   └──────────────┬──────────────────────────┘                  │
│                  │                                              │
│       ┌──────────┴──────────┐                                  │
│       ▼                     ▼                                  │
│  SQL_Database_Tool    Vector_Database_Tool                      │
│  (quantitative)       (semantic / RAG)                          │
│       │                     │                                  │
│       │              Pinecone Index                             │
│       │          (argo-floats-india, 384-dim)                   │
│       │              SentenceTransformer                        │
│       │              LangChain QA Chain                         │
│       │                                                         │
│       └──► POST /api/getsqldata ──► Backend ──► PostgreSQL     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Repository Map

```
SIH25/
├── FloatChat-Brain/       ← THIS REPO — AI Brain (Python/Flask)
├── FloatChat-Backend/     ← TypeScript API server
└── FloatChat-Frontend/    ← React + Vite SPA (float-landing-page)
```

---

## 🧠 This Repo — FloatChat-Brain (AI Orchestration)

This is the **intelligence layer** of FloatChat. It is a Python Flask server hosting a LangChain ReAct agent that decides which tool to use for each query, calls it, and synthesizes a structured JSON response.

### Project Structure

```
FloatChat-Brain/
│
├── run.py                        # Flask entry point — port 5000
├── embed.py                      # One-time pipeline: CSV → embeddings → Pinecone
├── cleaned_metadata[1].csv       # Raw ARGO metadata (40 fields, 75k+ records)
│
└── app/
    ├── __init__.py               # App factory — registers blueprints, inits vector service
    ├── config.py                 # Loads .env into Flask app.config
    │
    ├── brain/
    │   ├── llm.py                # LLM instance (Gemini / OpenAI)
    │   └── agent_prompts.py      # Full ReAct system prompt with domain rules
    │
    ├── controllers/
    │   ├── llm_controller.py     # Agent init, tool wrappers, response parser
    │   └── data_controller.py    # NetCDF/CSV file insert handler
    │
    ├── services/
    │   ├── sqldb_service.py      # HTTP proxy → Backend + direct PostgreSQL uploader
    │   └── vector_service.py     # Pinecone init, embedding, RAG QA
    │
    ├── routes/
    │   ├── llm_routes.py         # POST /api/llm/query
    │   └── data_routes.py        # POST /api/data/insert
    │
    └── schemas/
        ├── sql_schema.py         # Pydantic: QueryInput, FilterField, AggregateField, OrderByField
        └── vector_schema.py      # Pydantic: VectorQueryInput
```

### How the ReAct Agent Works

```
User Query
    │
    ▼
Thought: Is this quantitative (numbers/dates) or qualitative (definitions/context)?
    │
    ├── Quantitative ──► SQL_Database_Tool
    │                        └── POST /api/getsqldata → Backend → PostgreSQL
    │
    └── Qualitative  ──► Vector_Database_Tool
                             └── Embed query → Pinecone search → LangChain QA
    │
    ▼
Observation: Parse tool result
    │
    ▼
Repeat if needed (multi-step reasoning)
    │
    ▼
Final Answer: { "answer_blocks": [ {type, content}, ... ] }
```

### Tool Selection Rules (from System Prompt)

| Query type | Tool used |
|---|---|
| Temperature, salinity, pressure numbers | `SQL_Database_Tool` |
| Float positions, filters, aggregations | `SQL_Database_Tool` |
| "How does an ARGO float work?" | `Vector_Database_Tool` |
| Project descriptions, PI info, cycles | `Vector_Database_Tool` |
| Mixed — needs both | Calls both in sequence |

### Data Ingestion Pipeline (`embed.py`)

`embed.py` is the one-time script that populates Pinecone:

1. Reads `cleaned_metadata[1].csv` — 40 ARGO metadata fields (project name, PI name, platform type, cycle number, data centre, calibration history, etc.)
2. Converts each row into a descriptive text block with fixed field order
3. Embeds each text using `all-MiniLM-L6-v2` (384-dim, fast on CPU)
4. Upserts vectors + metadata into the `argo-floats-india` Pinecone index
5. Supports resume from any row index

### Schemas

**SQL Query Schema** (`sql_schema.py`):
```python
QueryInput:
  operation: "find" | "aggregate" | "count" | "groupBy"
  filters?:   [{ field, op: "=" | ">" | "<" | ">=" | "<=" | "between" | "in", value }]
  aggregates?: [{ field, fn: "count" | "avg" | "sum" | "min" | "max" }]
  orderBy?:   [{ field, direction: "asc" | "desc" }]
  groupBy?:   [field, ...]
  select?:    [field, ...]
  limit?:     int
```

**Vector Query Schema** (`vector_schema.py`):
```python
VectorQueryInput:
  query: str        # search text
  top_k?: int       # number of results (default 5)
```

### Agent Response Format

Every response from the Brain is a structured JSON:

```json
{
  "agent_thought_process": [ ... ],
  "final_answer": {
    "status": "success",
    "message": "Response processed successfully.",
    "answer_blocks": [
      { "type": "text",  "content": { "message": "The average salinity is 34.7 PSU." } },
      { "type": "table", "content": { "headers": ["Date", "Temp (°C)"], "rows": [...] } }
    ]
  }
}
```

---

## ⚙️ FloatChat-Backend (TypeScript API + Database)

**Repo:** [https://github.com/Hiten1007/FloatChat-Backend](https://github.com/Hiten1007/FloatChat-Backend)

The backend is the **data and routing engine**. It is a TypeScript/Express server running on port 3000. It serves two purposes:

1. **Acts as a public-facing gateway** — the frontend talks only to the backend, never directly to the Python Brain
2. **Runs all structured SQL queries** via Prisma ORM against PostgreSQL

### Project Structure

```
FloatChat-Backend/
│
├── src/
│   ├── index.ts                  # Express server entry (port 3000), CORS, route registration
│   ├── config.ts                 # Reads PORT, ISSUER_BASE_URL, AUDIENCE from env
│   │
│   ├── Controllers/
│   │   ├── llmcontrollers.ts     # getFloatData (SQL), getAnswer (proxy to Brain)
│   │   └── datacontrollers.ts    # insertIntoDB (file proxy to Brain)
│   │
│   ├── Routes/
│   │   ├── llmroutes.ts          # POST /api/getsqldata, POST /api/query
│   │   └── dataroutes.ts         # POST /insertdata/insert (multer file upload)
│   │
│   └── middleware/
│       ├── error-handler.ts      # Handles UnauthorizedError + generic 500
│       └── authenticate-user.ts  # JWT auth middleware (express-oauth2-jwt-bearer)
│
└── prisma/
    └── schema.prisma             # FloatData model + PostgreSQL datasource
```

### Database Schema (Prisma)

```prisma
model FloatData {
  id              Int       @id @default(autoincrement())
  platform_code   Int
  date_time       DateTime
  latitude        Float
  longitude       Float
  pres_adjusted   Float?    // Pressure in decibars
  temp_adjusted   Float?    // Temperature in °C
  psal_adjusted   Float?    // Practical salinity (PSU)
  dox2_adjusted   Float?    // Dissolved oxygen
  cphl_adjusted   Float?    // Chlorophyll-a
  bbp700_adjusted Float?    // Backscatter at 700nm
  fluo_adjusted   Float?    // Fluorescence
}
```

### Key Controllers

**`getFloatData`** — The SQL engine. Accepts a JSON query plan and executes it via Prisma:

| Operation | What it does |
|---|---|
| `find` | `prisma.floatData.findMany()` with filters, select, orderBy, limit |
| `aggregate` | `prisma.floatData.aggregate()` — avg, sum, min, max, count per field |
| `count` | `prisma.floatData.count()` with optional filters |
| `groupBy` | `prisma.floatData.groupBy()` with aggregate functions |

Field validation is enforced via an `ALLOWED_FIELDS` allowlist — no SQL injection possible.

**`getAnswer`** — The LLM proxy. Forwards the user's query to the Python Brain at `http://localhost:5000/api/llm/query` using `undici` with no timeout (agent reasoning can take time). Normalises the response into the `answer_blocks` envelope before returning to the frontend.

**`insertIntoDB`** — File proxy. Receives multipart file uploads (NetCDF/CSV) via `multer` (in-memory storage) and forwards them to the Brain's `/api/data/insert` endpoint via `axios`.

### Backend API Endpoints

| Method | Path | Controller | Description |
|---|---|---|---|
| `GET` | `/` | — | Health check — `{ status: "ok" }` |
| `POST` | `/api/getsqldata` | `getFloatData` | Execute a structured SQL query via Prisma |
| `POST` | `/api/query` | `getAnswer` | Forward NL query to Brain, return answer_blocks |
| `POST` | `/insertdata/insert` | `insertIntoDB` | Upload file and forward to Brain for ingestion |

### Backend Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| TypeScript | 5.5 | Language |
| Express | 5.1 | HTTP server |
| Prisma | 6.15 | ORM + query builder |
| PostgreSQL | — | ARGO measurements database |
| undici | 7.16 | HTTP client with no-timeout agent for LLM calls |
| multer | 2.0 | In-memory multipart file handling |
| cors | 2.8 | Cross-origin resource sharing |
| express-oauth2-jwt-bearer | 1.7 | JWT authentication middleware |
| dotenv | 17.2 | Environment variable loading |

---

## 🌐 float-landing-page (React Frontend)

**Repo:** [https://github.com/Hiten1007/float-landing-page](https://github.com/Hiten1007/float-landing-page)

The frontend is a **React 18 + Vite SPA** built with TypeScript and TailwindCSS. It is the user-facing layer — a rich, animated web application with a 3D ocean hero, feature sections, a live chat UI, and an embedded Streamlit map dashboard.

### Project Structure

```
FloatChat-Frontend/
│
├── index.html
├── vite.config.ts
├── tailwind.config.js
│
└── src/
    ├── App.tsx                   # Root — view router (landing | chat | dashboard)
    ├── main.tsx                  # React DOM entry
    ├── index.css                 # Global styles, typography tokens
    │
    ├── components/
    │   ├── Navigation.tsx        # Fixed navbar — scroll-aware glassmorphism, mobile menu
    │   ├── Hero.tsx              # Full-screen hero with 3D Ocean + animated CTA buttons
    │   ├── Ocean3D.tsx           # Three.js canvas — animated waves, particles, marine life
    │   ├── Features.tsx          # 6-feature grid (NL Queries, RAG, NetCDF, MCP, etc.)
    │   ├── Stats.tsx             # ARGO stats, data highlights section
    │   ├── ChatPage.tsx          # Full-screen AI chat UI (672 lines)
    │   ├── DashBoard.tsx         # Embeds external Streamlit map dashboard in iframe
    │   ├── FloatingChatButton.tsx # Persistent floating "Chat with AI" button
    │   ├── footer.tsx            # Footer
    │   └── TypographyShowcase.tsx # Design system showcase
    │
    └── types/                    # Shared TypeScript type definitions
```

### App Views

The app uses a simple state-based router with three views:

```
AppView: 'landing' | 'chat' | 'dashboard'

landing  → Navigation + Hero + Features + Stats + Footer + FloatingChatButton
chat     → Full-screen ChatPage
dashboard → Navigation + StreamlitDashboard (iframe embed)
```

### 3D Ocean Hero (`Ocean3D.tsx`)

Built with `@react-three/fiber` and Three.js:
- **OceanWaves** — animated `PlaneGeometry` with per-vertex sine wave displacement using `useFrame`
- **FloatingParticles** — 2000 particles rendered via `Points` + `PointMaterial`, rotating continuously
- **MarineLife** — 8 animated sphere meshes orbiting in 3D space
- Fog, directional light, and ambient light for depth

### Chat UI (`ChatPage.tsx`)

The chat is a **672-line production component** with:

- **Real-time API integration** — POSTs to `http://localhost:3000/api/query`
- **Fallback generator** — if the API is unavailable, uses a local `generateAIResponse()` function with 5 pre-built ARGO scenarios
- **Block-based rendering** — parses `answer_blocks` from the Brain and renders them as:
  - `TextBlock` — `whitespace-pre-wrap` text bubbles
  - `TableBlock` — scrollable data tables with alternating row colours, handles `headers+rows` or `dataObjects` format
  - `float_info` blocks — structured float detail cards (ID, status, distance, temperature, salinity)
  - `data` blocks — colour-coded metric rows (warning/error/success/info)
- **Example queries** — 5 clickable pre-set questions for ARGO data exploration
- **Animated loading** — 3-dot bounce animation while waiting for the Brain
- **Framer Motion** — `AnimatePresence` for message enter/exit animations

### Features Section (`Features.tsx`)

Six platform capabilities showcased:

| Feature | Description |
|---|---|
| Natural Language Queries | Ask in plain English, get AI-powered answers |
| Real-time Visualizations | Interactive charts from live data queries |
| RAG-Powered AI | Pinecone vector search for contextual accuracy |
| NetCDF Processing | Handles complex ARGO oceanographic formats |
| Global Coverage | Worldwide ARGO network with Indian Ocean focus |
| MCP Integration | Model Context Protocol for structured AI interactions |

### Frontend Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| React | 18.3 | UI library |
| TypeScript | 5.5 | Type safety |
| Vite | 7.1 | Build tool and dev server |
| TailwindCSS | 3.4 | Utility-first styling |
| Framer Motion | 11.0 | Animations and transitions |
| Three.js | 0.160 | 3D rendering engine |
| @react-three/fiber | 8.15 | React renderer for Three.js |
| @react-three/drei | 9.92 | Three.js helpers (Points, PointMaterial) |
| lucide-react | 0.344 | Icon library |
| @supabase/supabase-js | 2.57 | Supabase client (auth/storage) |

---

## 🔄 End-to-End Data Flow

### Chat Query Flow

```
1. User types query in ChatPage.tsx
2. POST http://localhost:3000/api/query  { "query": "..." }
3. Backend getAnswer() → forward to Brain POST http://localhost:5000/api/llm/query
4. Brain llm_routes.py → run_mcp_agent_flow(user_query)
5. LangChain ReAct Agent thinks:
     a. SQL query? → sql_tool_wrapper() → POST http://localhost:3000/api/getsqldata
        Backend getFloatData() → Prisma → PostgreSQL → return rows
     b. Semantic query? → vector_tool_wrapper() → SentenceTransformer encode
        → Pinecone index.query() → retrieve docs → LangChain QA chain → answer
6. Agent formats Final Answer as { "answer_blocks": [...] }
7. Brain parses + returns JSON to Backend
8. Backend normalises → returns to Frontend
9. ChatPage renderBotResponse() → renders TextBlock / TableBlock / cards
```

### File Upload Flow

```
1. User uploads NetCDF/CSV via Frontend
2. POST http://localhost:3000/insertdata/insert (multipart form)
3. Backend datacontrollers.ts → in-memory buffer via multer
   → axios POST http://localhost:5000/api/data/insert
4. Brain data_controller.py → processes file → inserts into PostgreSQL
```

---

## 🛠 Complete Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 18, TypeScript, Vite | SPA framework |
| **3D Graphics** | Three.js, @react-three/fiber | Interactive ocean visualization |
| **Animations** | Framer Motion | Smooth UI transitions |
| **Styling** | TailwindCSS | Utility-based design system |
| **API Gateway** | Express 5, TypeScript | Backend HTTP server |
| **ORM** | Prisma 6 | Type-safe PostgreSQL queries |
| **Database** | PostgreSQL | ARGO measurement storage |
| **AI Framework** | LangChain (ReAct) | Agent reasoning loop |
| **LLM** | Google Gemini / OpenAI | Language model |
| **Vector DB** | Pinecone | Semantic search index |
| **Embeddings** | all-MiniLM-L6-v2 | 384-dim sentence vectors |
| **AI Backend** | Python Flask | AI orchestration server |
| **Validation** | Pydantic v2 | Schema enforcement |
| **HTTP Client** | undici (TS), requests (Python) | Internal service communication |
| **File Handling** | multer, FormData | NetCDF/CSV file uploads |

---

## 🚀 Getting Started — Run the Full System

You need all three services running simultaneously.

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL database
- Pinecone account with an index named `argo-floats-india` (dimension: 384)
- Google Gemini or OpenAI API key

### 1. Start the Backend (TypeScript — Port 3000)

```bash
git clone https://github.com/Hiten1007/FloatChat-Backend.git
cd FloatChat-Backend
npm install
# Create .env (see Environment Variables section)
npm start
```

### 2. Start the Brain (Python Flask — Port 5000)

```bash
git clone https://github.com/Hiten1007/FloatChat-Brain.git
cd FloatChat-Brain
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Create .env (see Environment Variables section)

# First time only — populate Pinecone vector index
python embed.py

# Start the server
python run.py
```

### 3. Start the Frontend (React/Vite — Port 5173)

```bash
git clone https://github.com/Hiten1007/float-landing-page.git
cd float-landing-page
npm install
npm run dev
```

Open **http://localhost:5173** to use FloatChat.

---

## 🔑 Environment Variables

### Brain (`FloatChat-Brain/.env`)

```env
# LLM
GOOGLE_API_KEY=your_gemini_api_key
# OR
OPENAI_API_KEY=your_openai_api_key

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key
```

### Backend (`FloatChat-Backend/.env`)

```env
PORT=3000
DATABASE_URL=postgresql://user:password@localhost:5432/floatchat

# JWT Auth (if using Auth0)
ISSUER_BASE_URL=https://your-domain.auth0.com
AUDIENCE=your-api-audience

# Brain service URL
LLM_SERVICE_URL=http://localhost:5000/api/llm/query
```

---

## 📡 API Reference

### Brain Endpoints (Port 5000)

| Method | Path | Body | Description |
|---|---|---|---|
| `POST` | `/api/llm/query` | `{ "query": "string" }` | Run NL query through ReAct agent |
| `POST` | `/api/data/insert` | multipart file | Ingest NetCDF/CSV into PostgreSQL |

### Backend Endpoints (Port 3000)

| Method | Path | Body | Description |
|---|---|---|---|
| `GET` | `/` | — | Health check |
| `POST` | `/api/query` | `{ "query": "string" }` | NL query (proxied to Brain) |
| `POST` | `/api/getsqldata` | QueryInput JSON | Direct structured SQL query |
| `POST` | `/insertdata/insert` | multipart file | File upload (proxied to Brain) |

### SQL Query Examples

```json
// Find 5 records for a platform
{ "operation": "find", "filters": [{ "field": "platform_code", "op": "=", "value": 2900765 }], "limit": 5 }

// Average temperature globally
{ "operation": "aggregate", "aggregates": [{ "field": "temp_adjusted", "fn": "avg" }] }

// Highest salinity ever recorded
{ "operation": "aggregate", "aggregates": [{ "field": "psal_adjusted", "fn": "max" }], "orderBy": [{ "field": "psal_adjusted", "direction": "desc" }], "limit": 1 }

// Count records in a lat/lon box
{ "operation": "count", "filters": [{ "field": "latitude", "op": "between", "value": [10, 25] }, { "field": "longitude", "op": "between", "value": [60, 80] }] }
```

---

<div align="center">

Built with ❤️ for **Smart India Hackathon 2025**

**[⚙️ FloatChat-Backend](https://github.com/Hiten1007/FloatChat-Backend)** &nbsp;·&nbsp; **[🌐 float-landing-page](https://github.com/Hiten1007/float-landing-page)**

</div>
