# Multi-Model LLM Comparator

Compare OpenAI, Gemini, and Claude using the same prompt and measure response
quality, latency, token usage, estimated cost, and reliability.

## What it demonstrates

- Provider adapters behind one application-owned interface
- Concurrent multi-provider inference with partial-failure handling
- Provider-native token accounting and centralized cost estimation
- SQLite for zero-setup development and PostgreSQL for deployment
- Persisted comparison history and five-dimension manual evaluation
- Safe public error codes, provider timeouts, retries, and input validation
- FastAPI/OpenAPI documentation and a network-free automated test suite
- Responsive React interface with provider selection, result cards, history,
  recommendation, and manual rating controls

## API

Start the backend and open `http://127.0.0.1:8000/docs`.

### Compare selected providers

```http
POST /api/v1/compare
Content-Type: application/json
```

```json
{
  "prompt": "Explain vector embeddings to a beginner.",
  "providers": ["gemini", "openai", "anthropic"]
}
```

The response contains normalized results, token usage, estimated cost, a
persisted comparison ID, and a preliminary recommendation. A provider failure
does not discard successful results from other providers.

### Other endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Service health |
| `POST` | `/api/v1/compare/gemini` | Gemini-only inference |
| `POST` | `/api/v1/compare/openai` | OpenAI-only inference |
| `POST` | `/api/v1/compare/claude` | Claude-only inference |
| `GET` | `/api/v1/compare/history` | Recent comparisons |
| `GET` | `/api/v1/compare/history/{id}` | One comparison |
| `PUT` | `/api/v1/compare/history/{id}/ratings/{provider}` | Manual rating |

## Local setup

Use Python 3.12 or 3.13.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Configure the real provider keys and model IDs in `backend/.env`, then run:

```powershell
uvicorn app.main:app --reload
```

The default database is `backend/comparator.db`. Set `DATABASE_URL` to a
PostgreSQL connection string for deployment:

```env
DATABASE_URL=postgresql+psycopg://comparator:password@localhost:5432/comparator
```

## Tests

```powershell
cd backend
python -m pytest -q -p no:cacheprovider
```

Tests mock provider SDKs and do not use API credits. The benchmark cases in
`benchmark-data/test-prompts.json` cover summarization, extraction,
instruction-following, reliability, classification, and generation.

## Frontend

The frontend uses React, TypeScript, and vinext. With Node.js 22.13 or newer:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`. The default API URL is
`http://localhost:8000`; it can be changed under **Connection settings** in
the interface. For a deployed frontend, configure the backend's
`CORS_ORIGINS` with the deployed site origin.

From the repository root on Windows, both servers can also be started with:

```powershell
.\run-local.ps1
```

## Cost estimates

Prices are maintained in `backend/app/services/cost_service.py`. Unknown model
IDs return `null` cost rather than an invented estimate. Verify pricing against
the provider's official pricing page before using estimates for budgeting.

## Architecture

See [docs/architecture.md](docs/architecture.md) and
[docs/learning-log.md](docs/learning-log.md).
