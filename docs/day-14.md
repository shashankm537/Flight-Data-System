# Day 14 — Metabase BI Dashboard
Date: 22-03-2026 | Branch: day-14

## Objective
Set up Metabase BI dashboard and deploy publicly on Railway.io.

## What Was Done
- Pulled metabase/metabase:latest Docker image locally
- Ran Metabase at localhost:3000
- Connected Metabase to Neon PostgreSQL
- Created Flight Delay Analytics dashboard with 4 charts
- Updated docker-compose.yml to include Metabase service
- Deployed Metabase on Railway.io
- Recreated all 4 charts on live Railway instance
- Enabled public sharing for dashboard

## Files Modified
| File | Purpose |
|---|---|
| `docker-compose.yml` | Added Metabase service + persistent volume |
| `README.md` | Added Metabase live URL |

## Live URLs
| Service | URL |
|---|---|
| Metabase | https://metabase-production-04c3.up.railway.app |
| Public Dashboard | https://metabase-production-04c3.up.railway.app/public/dashboard/8b35977b-89c0-4b1d-a935-5a951d6bf9b1 |

## Pending
- None