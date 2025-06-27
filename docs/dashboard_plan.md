# Generation Dashboard Plan

## Overview

This document describes the architecture and implementation plan for a lightweight web-based “Generation Dashboard” that lets stakeholders watch live progress of the requirements-generation orchestrator and estimate when the run will complete.

## UI Requirements & Design

* Real-time status of every document (state, size, refinement count, timestamps)  
* Overall progress bar & ETA based on average document duration  
* Live log window to read orchestrator messages (stream or tail)  
* Dependency graph image & traceability graph thumbnails  
* Runs locally with no external cloud services required

## High-Level Architecture

The dashboard is split into a Python **Backend** that serves data over WebSocket & REST, and a **Front-End** single-page application built with React + Vite.

```mermaid
flowchart TD
    subgraph Backend [Python FastAPI + WebSocket]
        A1[orchestrator.py] --writes JSON status--> A2[status_dir/*.json]
        B1[FastAPI server] --reads & streams--> WS[[WebSocket]]
        B2[/api/summary] --REST--> FrontEnd
    end
    subgraph FrontEnd [React + Vite]
        WS ==> C1[Redux store]
        C1 --> C2[Progress Table]
        C1 --> C3[Overall Progress Bar & ETA]
        C1 --> C4[Live Log Panel]
        C1 --> C5[Graphs (img tags)]
    end
```

### Data Flow

1. `orchestrator.py` already writes a `status_dir` file per document (JSON or YAML).  
2. **Backend** polls that directory every *N* seconds (default 2 s) and builds an in-memory model.  
3. Any change is broadcast over the `/ws/status` WebSocket channel as a small diff payload.  
4. **Front-end** maintains a Redux (or Zustand) store fed by the socket; components re-render instantly.  
5. The front-end can refresh or first load via `/api/summary` REST endpoint.  

## Component Details

| Layer    | File/Folder                               | Purpose                                   |
|----------|-------------------------------------------|-------------------------------------------|
| Backend  | `backend/app.py`                          | FastAPI application with WebSocket + REST |
|          | `backend/status_reader.py`                | Re-uses logic from `monitor.py` to parse status files |
|          | `backend/models.py`                       | Pydantic schemas for status payloads      |
| Frontend | `frontend/`                               | Vite + React project                      |
|          | `frontend/src/components/StatusTable.tsx` | Tabular view with emoji statuses          |
|          | `frontend/src/components/OverallProgress.tsx` | Circular progress + ETA               |
|          | `frontend/src/components/LogPanel.tsx`    | Live log tail                             |
| DevOps   | `package.json` scripts                    | `npm run dev`, `npm run build`            |

### Backend Endpoints

| Method | Path            | Description                                      |
|--------|-----------------|--------------------------------------------------|
| WS     | `/ws/status`    | Push JSON diff whenever status changes           |
| GET    | `/api/summary`  | Current full snapshot for page refresh           |
| GET    | `/app`          | Serves SPA (built files) in production           |

### ETA Algorithm

*Track the average duration per document so far:*  

```
eta = (remaining_documents) × (sum(elapsed_durations) / completed_documents)
```

This provides a simple but useful forecast; future enhancement: maintain averages per document type.

## Implementation Steps

1. **Create folder `dashboard/`** with two sub-folders: `backend/` and `frontend/`.  
2. **Backend**  
   * Add FastAPI + Uvicorn dependency to `requirements.txt`.  
   * Implement `backend/app.py` (~100 LoC) with polling & WebSocket.  
   * Unit-test status parsing with sample JSON.  
3. **Front-End**  
   * Scaffold with `npm create vite@latest` → React + TS template.  
   * Install Chakra UI (or MUI) and Redux Toolkit.  
   * Build components listed above (~300 LoC).  
   * Add reconnect & toast warnings on disconnect.  
4. **Integrate** – during dev use `npm run dev` (Vite) + `uvicorn backend.app:app --reload`.  
5. **Build** – `npm run build` outputs static files; backend serves them via StaticFiles middleware.  

## Dependencies

**Python**: `fastapi`, `uvicorn[standard]`, `pydantic`, `watchfiles`, `rich`  
**JavaScript**: `react`, `react-dom`, `@chakra-ui/react` (or `@mui/material`), `@reduxjs/toolkit`, `vite`

## Estimated Effort

* Backend ≈ 100 LoC / 0.5 – 1 hr  
* Front-End ≈ 300 LoC / 1 – 2 hr  
* Testing & polish ≈ 0.5 hr  

## Future Improvements

* Per-document-type ETA algorithm  
* Email / Slack notifications on completion or failure  
* Authentication if exposing beyond localhost  

---

*Approved on 2025-06-10 by Stakeholder; proceed to implementation.*