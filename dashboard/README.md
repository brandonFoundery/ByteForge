# Requirements Generation Dashboard

A real-time monitoring dashboard for the FY.WB.Midway Requirements Generation System.

![Dashboard Screenshot](https://via.placeholder.com/800x450?text=Requirements+Generation+Dashboard)

## Overview

This dashboard provides a visual interface to monitor the progress of the requirements generation process. It shows real-time status updates, document generation progress, and logs from the orchestrator.

## What's Included

1. **Backend System (FastAPI)**
   - Status monitoring service that reads document metadata
   - REST API endpoints for data retrieval
   - Real-time log streaming

2. **Dashboard Interface**
   - Simple HTML dashboard that works without npm/React setup
   - Progress tracking with ETA calculation
   - Document status table with detailed information
   - Live log streaming panel

3. **Utility Scripts**
   - `setup_demo.py` - Creates sample data for testing
   - `run_simple.py` - Runs the backend server
   - `open_dashboard.py` - Opens the dashboard in a browser
   - `test_api.py` - Tests API connectivity

## Features

- **Real-time Status Updates**: See the current status of each document being generated
- **Progress Tracking**: Overall progress bar with ETA calculation
- **Document Table**: Detailed view of all documents with their status, size, and refinement count
- **Live Logs**: Stream of log messages from the orchestrator
- **Simple HTML Version**: No npm or React setup required

## Quick Start

### Option 1: Simple HTML Dashboard (Recommended)

1. **Setup demo data** (if needed):
   ```bash
   python setup_demo.py
   ```

2. **Start the backend server**:
   ```bash
   python run_simple.py
   ```

3. **Open the dashboard**:
   ```bash
   python open_dashboard.py
   ```

This will open the dashboard in your default web browser. The dashboard will automatically connect to the backend server and display the current status.

### Option 2: Full React Dashboard (Advanced)

If you have Node.js and npm installed, you can run the full React dashboard:

1. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start the backend server**:
   ```bash
   python run_simple.py
   ```

3. **Start the frontend development server**:
   ```bash
   cd frontend
   npm run dev
   ```

4. **Open the dashboard** in your browser at http://localhost:5173

## Troubleshooting

### Backend Issues

If you're having issues with the backend server:

1. **Check if the server is running**:
   ```bash
   python test_api.py
   ```

2. **Verify sample data**:
   ```bash
   python setup_demo.py
   ```

3. **Check the output directories**:
   - Status files should be in: `d:/Repository/@Clients/FY.WB.Midway/generation_status`
   - Document files should be in: `d:/Repository/@Clients/FY.WB.Midway/generated_documents`

### Frontend Issues

If you're having issues with the frontend:

1. **Use the simple HTML dashboard**:
   ```bash
   python open_dashboard.py
   ```

2. **Check browser console** for any JavaScript errors

3. **Verify API connectivity**:
   ```bash
   python test_api.py
   ```

## Architecture

The dashboard consists of two main components:

1. **Backend (FastAPI)**: 
   - Monitors the status directory for changes
   - Provides REST API endpoints for data access
   - Located in `dashboard/backend/`

2. **Frontend**:
   - **Simple HTML Version**: Single HTML file with JavaScript (`simple_dashboard.html`)
   - **React Version**: Full React application with TypeScript and Material-UI (in `frontend/`)

## Files

```
dashboard/
├── backend/                # FastAPI backend
│   ├── app.py             # Main FastAPI application
│   ├── models.py          # Data models
│   └── status_reader.py   # Status file parser
├── frontend/              # React frontend (optional)
├── sample_data/           # Sample data for testing
│   ├── status_BRD.json    # Sample status files
│   ├── status_PRD.json
│   ├── status_FRD.json
│   └── orchestrator.log   # Sample log file
├── simple_dashboard.html  # Standalone HTML dashboard
├── open_dashboard.py      # Script to open HTML dashboard
├── run_simple.py          # Script to run backend server
├── setup_demo.py          # Script to set up demo data
├── test_api.py            # Script to test API endpoints
└── README.md              # This file
```

## Development

To modify the dashboard:

- **Backend**: Edit files in `dashboard/backend/`
- **Simple HTML Dashboard**: Edit `simple_dashboard.html`
- **React Dashboard**: Edit files in `frontend/src/`

## License

MIT

## Implementation Details

- **Total Files**: 36 files added in the dashboard implementation
- **Lines of Code**: 7,196 lines of code added
- **Git Commit**: All changes committed with message "feat: Add requirements generation dashboard with real-time monitoring"
- **Key Technologies**: FastAPI, Python, HTML/CSS/JavaScript, Bootstrap

## Key Features

- **Real-time Updates**: The dashboard polls the backend every few seconds
- **Progress Tracking**: Shows completion percentage and ETA
- **Document Status**: Displays status, size, and refinement count for each document
- **Log Streaming**: Shows real-time logs from the generation process
- **Simple Setup**: Works with just Python, no npm required