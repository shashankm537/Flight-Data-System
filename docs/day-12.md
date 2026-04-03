# Day 12 — Fix Render Deployment + Streamlit Cloud
Date: 22-03-2026 | Branch: day-12

## Objective
Resolve Render deployment failure and get both FastAPI and Streamlit live.

## What Was Done
- Changed pandas==2.2.0 to pandas==2.2.3 in requirements.txt
- Pinned pyarrow==14.0.2 to avoid build-from-source failure
- Added PYTHON_VERSION=3.12.3 as environment variable in Render
- Deployed FastAPI successfully on Render
- Deployed Streamlit on Streamlit Community Cloud
- Added DATABASE_URL and API_URL secrets in Streamlit Cloud

## Files Modified
| File | Purpose |
|---|---|
| `requirements.txt` | pandas 2.2.0→2.2.3, added pyarrow==14.0.2 |

## Errors Fixed
| Error | Fix |
|---|---|
| Render using Python 3.14 despite runtime.txt | Added PYTHON_VERSION=3.12.3 env var |
| pyarrow failing to build from source | Pinned pyarrow==14.0.2 |

## Live URLs
| Service | URL |
|---|---|
| FastAPI | https://flight-data-system-q1an.onrender.com |
| Streamlit | https://flight-data-system.streamlit.app |

## Dashboard Metrics
| Metric | Value |
|---|---|
| Total Flights | 7,882 |
| Delayed Flights | 1,830 |
| Delay Rate | 23.22% |
| Avg Delay | 8.49 mins |

## Pending
- README.md update with live URLs