"""
FastAPI app with SSE streaming endpoint.
"""

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from backend.agent import stream_chat

# Create FastAPI app instance 
app = FastAPI(title="Pharmacy Agent")

# CORS (Cross-Origin Resource Sharing) for local development - allows cross-origin requests between frontend and backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # All origins (dev only)
    allow_methods=["*"],    # All HTTP methods
    allow_headers=["*"],    # All headers
)

# Define the path to the frontend directory
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


@app.post("/chat")
async def chat(request: Request):
    """SSE endpoint — receives messages, streams response."""
    # Extract messages from the body 
    body = await request.json() 
    messages = body.get("messages", []) 
    
    def generate():
        # Generate response events from stream_chat function
        for event in stream_chat(messages):
            yield event
    
    return StreamingResponse(generate(), media_type="text/event-stream")    # Return streaming response


@app.get("/")
async def index():
    """Serve the chat UI."""
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
async def health():
    """Health check for Docker."""
    return {"status": "ok"}