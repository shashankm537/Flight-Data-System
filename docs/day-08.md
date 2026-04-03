# Day 8 — Docker Containerization
Date: 16-03-2026 | Branch: day-8

## Objective
Containerize FastAPI and Streamlit for consistent deployment.

## What Was Done
- Created Dockerfiles for FastAPI and Streamlit
- Built Docker Compose to orchestrate both services
- Created .dockerignore to exclude unnecessary files
- Tested both containers running together

## Files Created
| File | Purpose |
|---|---|
| `api/Dockerfile` | FastAPI container |
| `dashboard/Dockerfile` | Streamlit container |
| `docker-compose.yml` | Orchestrates both services |
| `.dockerignore` | Excludes venv, mlruns, pkl |

## Errors Fixed
| Error | Fix |
|---|---|
| Docker not installed | Installed Docker Desktop v4.64.0 |
| WSL outdated | Updated to WSL 2.6.3 |

## Results
- ✅ Both containers running — localhost:8501 and localhost:8000

## Pending
- None