# Recruitment Platform — Documentation

Recruitment Platform is a **Python / FastAPI** application (not a Node.js
stack). This directory holds supporting documentation; the project overview and
quick start live in [`../README.md`](../README.md).

## What this project actually is

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 (CI/Docker); `requires-python >=3.10` |
| Framework | FastAPI + Uvicorn |
| Validation | Pydantic v2 + pydantic-settings |
| Persistence | SQLAlchemy 2.0 — SQLite by default (`DATABASE_URL=sqlite:///./recruitment.db` in `.env.example`) |
| Cache / queue | Redis URL supported (`REDIS_URL`); in-process by default |
| Auth | JWT (`python-jose`) |
| Tests | pytest — suite in top-level `tests/` (267 tests) |
| Deploy | Docker, docker-compose, k8s (kustomize), Helm, Terraform |

## Entrypoint & health

```bash
# Local dev entrypoint (runs uvicorn recruitment_platform.main:app)
python -m recruitment_platform.main

# Health check (root) — also /api/health and /api/ready
curl http://localhost:8000/health
```

The API router is mounted at **`/api`** (there is no `/api/v1` prefix for the
application's own routers).

## Documentation index

| Document | Description |
|----------|-------------|
| [../README.md](../README.md) | Project overview, features, API summary |
| [API.md](./API.md) | API reference |
| [api-reference.md](./api-reference.md) | Extended endpoint specifications |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Deployment guide |
| [deployment-guide.md](./deployment-guide.md) | Deployment guide (detailed) |
| [development-guide.md](./development-guide.md) | Local development workflow |
| [architecture.md](./architecture.md) | Architecture overview |
| [user-guide.md](./user-guide.md) | End-user guide |
| [GAP_ANALYSIS.md](./GAP_ANALYSIS.md) | Gap analysis notes |
| [adr/](./adr/) | Architecture decision records |
