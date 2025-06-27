"""
FastAPI backend for the Requirements Generation Dashboard
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import asyncio
import json
from datetime import datetime
from typing import List, Optional
import uvicorn

from .models import GenerationSummary, StatusUpdate, LogEntry
from .status_reader import StatusReader


app = FastAPI(title="Requirements Generation Dashboard API")

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
status_reader: Optional[StatusReader] = None
connected_websockets: List[WebSocket] = []
background_task = None

# Configuration
OUTPUT_PATH = Path("d:/Repository/@Clients/FY.WB.Midway/generated_documents")
STATUS_PATH = Path("d:/Repository/@Clients/FY.WB.Midway/generation_status")
POLL_INTERVAL = 2  # seconds


@app.on_event("startup")
async def startup_event():
    """Initialize the status reader and start background polling"""
    global status_reader, background_task
    
    # Initialize status reader
    status_reader = StatusReader(OUTPUT_PATH, STATUS_PATH)
    
    # Start background polling task
    background_task = asyncio.create_task(poll_status_updates())
    
    print(f"Dashboard API started. Monitoring: {OUTPUT_PATH}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up background tasks"""
    global background_task
    if background_task:
        background_task.cancel()


async def poll_status_updates():
    """Background task to poll for status changes"""
    last_summary = None
    
    while True:
        try:
            # Get current summary
            current_summary = status_reader.get_summary()
            
            # Check if there are changes
            if current_summary != last_summary:
                # Broadcast update to all connected clients
                update = StatusUpdate(
                    timestamp=datetime.now(),
                    summary=current_summary,
                    message="Status updated"
                )
                
                await broadcast_update(update)
                last_summary = current_summary
            
            # Also check for new logs
            logs = status_reader.read_logs(last_n_lines=10)
            if logs:
                # Send recent logs (implementation depends on log format)
                pass
                
        except Exception as e:
            print(f"Error in polling task: {e}")
            
        await asyncio.sleep(POLL_INTERVAL)


async def broadcast_update(update: StatusUpdate):
    """Broadcast update to all connected WebSocket clients"""
    disconnected = []
    
    for websocket in connected_websockets:
        try:
            await websocket.send_json(update.dict())
        except Exception:
            disconnected.append(websocket)
    
    # Remove disconnected clients
    for ws in disconnected:
        if ws in connected_websockets:
            connected_websockets.remove(ws)


@app.get("/api/summary", response_model=GenerationSummary)
async def get_summary():
    """Get current generation summary"""
    if not status_reader:
        return GenerationSummary()
    
    return status_reader.get_summary()


@app.get("/api/logs")
async def get_logs(last_n: int = 100):
    """Get recent log entries"""
    if not status_reader:
        return {"logs": []}
    
    logs = status_reader.read_logs(last_n_lines=last_n)
    return {"logs": logs}


@app.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time status updates"""
    print("WebSocket connection request received")
    
    try:
        await websocket.accept()
        print("WebSocket connection accepted")
        
        connected_websockets.append(websocket)
        
        # Send initial summary
        if status_reader:
            summary = status_reader.get_summary()
            update = StatusUpdate(
                timestamp=datetime.now(),
                summary=summary,
                message="Connected to dashboard"
            )
            await websocket.send_json(update.dict())
            print("Initial summary sent")
        
        # Keep connection alive
        while True:
            # Wait for any message from client (ping/pong)
            data = await websocket.receive_text()
            print(f"Received message: {data}")
            
            # Echo back as pong
            if data == "ping":
                await websocket.send_text("pong")
                print("Sent pong response")
                
    except WebSocketDisconnect:
        print("WebSocket disconnected normally")
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)


# Serve static files in production
static_path = Path(__file__).parent.parent / "frontend" / "dist"
if static_path.exists():
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")


def main():
    """Run the dashboard server"""
    import sys
    import os
    
    # Allow custom paths via command line
    if len(sys.argv) > 1:
        global OUTPUT_PATH
        OUTPUT_PATH = Path(sys.argv[1])
    
    if len(sys.argv) > 2:
        global STATUS_PATH  
        STATUS_PATH = Path(sys.argv[2])
    
    # Ensure paths exist
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.mkdir(parents=True, exist_ok=True)
    
    # Run server
    uvicorn.run(
        "dashboard.backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()