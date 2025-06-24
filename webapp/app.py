import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import asyncio

from perplexity_async import Client as PerplexityClient

BASE_DIR = os.path.dirname(__file__)

app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

class ChatRequest(BaseModel):
    provider: str | None = None
    model: str | None = None
    message: str
    conversation_id: str | None = None

perplexity_cli: PerplexityClient | None = None

@app.on_event("startup")
async def startup_event():
    global perplexity_cli
    perplexity_cli = await PerplexityClient()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat/send")
async def chat_send(data: ChatRequest):
    if not perplexity_cli:
        raise RuntimeError("Perplexity client not initialized")
    resp = await perplexity_cli.search(
        data.message,
        mode=data.provider or "auto",
        model=data.model,
    )
    return resp

@app.get("/api/proxy_status")
async def proxy_status():
    return {"status": "online"}

AVAILABLE_MODELS = {
    "auto": [None],
    "pro": [None, "sonar", "gpt-4.5", "gpt-4o", "claude 3.7 sonnet", "gemini 2.0 flash", "grok-2"],
    "reasoning": [None, "r1", "o3-mini", "claude 3.7 sonnet"],
    "deep research": [None],
}

@app.get("/proxy/models/{provider}")
async def models(provider: str):
    return {"models": AVAILABLE_MODELS.get(provider, [])}
