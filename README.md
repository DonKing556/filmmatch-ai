# FilmMatch AI

A concise, friendly movie recommendation engine that helps people quickly choose a movie — solo or with friends. Reduces decision fatigue and gets you to a confident "let's watch this" in under 90 seconds.

## Features

- **Solo Mode** — Get personalized recommendations based on your taste: genres, actors, directors, mood, era, and constraints.
- **Group Mode** — Find the perfect movie for everyone. Identifies overlap, respects dealbreakers, and ranks by group fit.
- **Fast Narrowing** — Interactive follow-ups that zero in on the right pick quickly.
- **Smart Scoring** — Transparent recommendation logic so you understand *why* a film was suggested.

## Tech Stack

| Layer    | Technology       |
|----------|------------------|
| Backend  | Python / FastAPI  |
| AI       | Claude API        |
| Frontend | React / TypeScript |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Deployment | Docker          |

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- An Anthropic API key

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your API key
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
filmmatch-ai/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # API endpoints
│   │   ├── core/             # Config, dependencies
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic & AI integration
│   │   └── prompts/          # System prompts & templates
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Route pages
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API client
│   │   └── types/            # TypeScript types
│   └── public/
├── docs/                     # Documentation
├── scripts/                  # Dev & deployment scripts
└── .github/                  # CI/CD & templates
```

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/api/v1/recommend` | Get movie recommendations |
| POST   | `/api/v1/recommend/group` | Group recommendation |
| POST   | `/api/v1/narrow` | Narrow down from previous results |
| GET    | `/api/v1/health` | Health check |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — see [LICENSE](LICENSE) for details.
