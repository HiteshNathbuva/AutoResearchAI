# AutoResearchAI

## Project Overview

AutoResearchAI is an Autonomous Multi-Agent Research Platform designed to conduct comprehensive research tasks through coordinated AI agents. The platform leverages multiple specialized agents working together to plan, research, verify, and generate high-quality research reports on any given topic.

## Vision

To create a fully autonomous research system that can:
- Decompose complex research queries into manageable sub-tasks
- Conduct thorough research using multiple sources and tools
- Verify information accuracy and credibility
- Synthesize findings into coherent, well-structured reports
- Maintain context and learn from previous research sessions

## Folder Structure

```
AutoResearchAI/
├── backend/
│   ├── api/           # API endpoints and routes
│   ├── core/          # Core business logic
│   ├── services/      # Service layer implementations
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic schemas for validation
│   └── utils/         # Utility functions
├── frontend/          # Frontend application
├── agents/            # AI agent implementations
├── tools/             # Research tools and integrations
├── prompts/           # Agent prompt templates
├── memory/
│   └── vectorstore/   # Vector database for memory storage
├── database/
│   └── sqlite/        # SQLite database files
├── reports/
│   └── generated/     # Generated research reports
├── config/            # Configuration files
├── tests/             # Test suites
├── docker/            # Docker configurations
├── docs/              # Documentation
│   ├── architecture.md
│   ├── workflow.md
│   └── roadmap.md
├── scripts/           # Utility scripts
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
└── LICENSE
```

## Technology Stack

- **Backend**: Python
- **Database**: SQLite
- **Memory**: Vector Database (TBD)
- **API**: (TBD)
- **Frontend**: (TBD)
- **AI/ML**: LLM-based agents via OpenRouter API
- **Search**: Brave Search API

## Roadmap

See [docs/roadmap.md](docs/roadmap.md) for detailed roadmap information.

## License

See [LICENSE](LICENSE) file for details.
