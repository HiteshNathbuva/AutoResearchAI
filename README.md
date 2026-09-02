<div align="center">

# 🧠 AutoResearchAI

### Production-Grade Multi-Agent AI Research Platform

Build intelligent research workflows using multiple AI agents, FastAPI, and OpenRouter.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Production-green?logo=fastapi)
![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM-orange)
![REST API](https://img.shields.io/badge/API-REST-red)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-blue)

</div>

---

# 📖 Overview

AutoResearchAI is a production-style Multi-Agent AI Research Platform designed to automate the complete research workflow.

Instead of relying on a single AI response, the system divides research into specialized AI agents that collaborate to produce higher-quality, structured, and verifiable results.

The project follows modern AI engineering practices including modular architecture, workflow orchestration, session management, REST APIs, and scalable backend design.

---

# ✨ Features

- 🤖 Multi-Agent AI Architecture
- 🧠 Planner Agent
- 🔍 Research Agent
- ✅ Verifier Agent
- 📝 Writer Agent
- 🌐 Real Web Research (search + safe fetching + source tracking)
- 🛡️ SSRF-protected web fetching
- 📑 Source tracking & citations
- ⚡ FastAPI Backend
- 🌐 REST API
- 🔄 Session-Based Workflow
- 📚 Professional Report Generation
- 📊 AI Fact Check
- 📄 Markdown Report
- 📑 PDF/DOCX Export (Coming Soon)
- 💬 Follow-up Research (Planned)

---

# 🏗 Architecture

```text
                    User
                      │
                      ▼
              FastAPI REST API
                      │
                      ▼
          Workflow Orchestrator
                      │
      ┌───────────────┼───────────────┐
      ▼               ▼               ▼
 Planner Agent   Research Agent   Session Manager
                      │
                      ▼
              Verification Agent
                      │
                      ▼
                Writer Agent
                      │
                      ▼
              Professional Report
```

---

# ⚙ Current Workflow

```text
User Query
      │
      ▼
Planner Agent (Hidden)
      │
      ▼
Research Agent
      │
      ▼
Research Results
      │
      ├──────────────► AI Fact Check
      │                    │
      │                    ▼
      │             Verifier Agent
      │                    │
      │                    ▼
      │             Verified Report
      │
      └──────────────► Generate Report
                           │
                           ▼
                      Writer Agent
                           │
                           ▼
                  Professional Report
```

---

# 🛠 Tech Stack

| Category | Technologies |
|----------|--------------|
| Language | Python |
| Backend | FastAPI |
| AI Provider | OpenRouter |
| AI Model | OpenRouter Auto |
| API Style | REST API |
| Configuration | Pydantic Settings |
| Validation | Pydantic |
| Server | Uvicorn |
| Version Control | Git + GitHub |

---

# 📂 Project Structure

```text
AutoResearchAI/

backend/
│
├── agents/
├── api/
├── core/
├── prompts/
├── schemas/
├── utils/
│
├── main.py
│
tests/
│
requirements.txt
README.md
```

---

# 🚀 API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | / | Health Check |
| POST | /research | Generate Research |
| POST | /verify/{session_id} | AI Fact Check |
| POST | /report/{session_id} | Generate Professional Report |

---

# 🚀 Getting Started

## Clone Repository

```bash
git clone https://github.com/hiteshnathbuva/AutoResearchAI.git

cd AutoResearchAI
```

## Create Virtual Environment

```bash
python -m venv .venv
```

Activate environment

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment

Create a `.env` file in the project root.

```env
OPENROUTER_API_KEY=your_api_key_here
```

### Optional: Real Web Research (Phase 2)

Web research is off by default. To enable it, set the following (all optional —
the app boots fine without them, and gracefully falls back to LLM-only research
if web tools are disabled or fail):

```env
# Enable real web research (default: false)
WEB_RESEARCH_ENABLED=true

# Search provider: auto | tavily | none (default: auto)
SEARCH_PROVIDER=auto

# Optional Tavily API key. Never commit a real key. When absent and search is
# enabled, the system degrades gracefully to LLM-only research.
TAVILY_API_KEY=your_tavily_key_here

# Bounded resource limits (safe defaults shown)
SEARCH_MAX_RESULTS=5
SEARCH_TIMEOUT_SECONDS=10
SEARCH_MAX_RETRIES=2
MAX_FETCHED_SOURCES=5
FETCH_TIMEOUT_SECONDS=10
FETCH_MAX_REDIRECTS=3
FETCH_MAX_BYTES=2000000
EXTRACT_MAX_CHARS=8000
```

**Security restrictions:** fetched URLs and every redirect are validated
against an SSRF blocklist *before* any connection. Only HTTP/HTTPS is allowed;
localhost, loopback, private/link-local/reserved networks, CGNAT, cloud-metadata
addresses, and common encoded-IP bypasses are rejected. Response size, redirect
count, and extracted text are all bounded, and fetched page content is treated as
untrusted data (never as instructions) in every prompt.

---

## Run Backend

```bash
python -m uvicorn backend.main:app --reload
```

Open

```
http://127.0.0.1:8000/docs
```

---

# 🗺 Roadmap

## ✅ Completed

- Multi-Agent Architecture
- Workflow Engine
- Planner Agent
- Research Agent
- Verifier Agent
- Writer Agent
- FastAPI Backend
- REST API
- Session Management
- Swagger Documentation

## 🚧 In Progress

- Repository Improvements
- React Frontend
- Professional Dashboard

## 🔮 Planned

- PDF Export
- DOCX Export
- Follow-up Research
- Visual Reports
- Internet Search Integration
- RAG Knowledge Base
- Authentication
- Conversation History
- Docker Deployment

---

# 🤝 Contributing

Contributions, issues, and feature requests are welcome.

Feel free to fork the project and submit pull requests.

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Hitesh Nathbuva**

GitHub

https://github.com/hiteshnathbuva

---

⭐ If you found this project useful, consider giving it a star.