# Day 11 — Render Deployment Attempt
Date: 22-03-2026 | Branch: day-11

## Objective
Deploy FastAPI live on the internet via Render.

## What Was Done
- Created Render account and connected GitHub repository
- Created FastAPI web service on Render
- Created runtime.txt to pin Python version to 3.12.3
- Diagnosed root cause: Render defaulting to Python 3.14.3

## Files Created
| File | Purpose |
|---|---|
| `runtime.txt` | Attempted to pin Python version for Render |

## Errors Fixed
| Error | Fix |
|---|---|
| Render defaulting to Python 3.14.3 | Created runtime.txt — did not work |
| pandas==2.2.0 incompatible with Python 3.14 | Identified fix: upgrade to pandas==2.2.3 |
| Git push rejected non-fast-forward | git fetch + git reset --hard origin/main |

## Results
- ✅ FastAPI service created on Render
- ❌ Build failing — pandas/Python incompatibility unresolved

## Pending
- Fix pandas version to 2.2.3
- Force Python 3.12 on Render