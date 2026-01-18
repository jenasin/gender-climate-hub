"""
FastAPI Backend pro Gender & Climate Intelligence Hub
"""

from dotenv import load_dotenv
import os

# Načti .env z parent složky
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import asyncio
from datetime import datetime

from agent import GenderClimateAgent, ThoughtStep
from data_banks import DataHub, COUNTRIES

app = FastAPI(
    title="Gender & Climate Intelligence Hub API",
    description="ReACT Agent s plánováním, výpočetními nástroji a historií",
    version="1.0.0"
)

# CORS pro React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5180", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globální instance
hub = DataHub()
_agent = None

def get_agent():
    global _agent
    if _agent is None:
        _agent = GenderClimateAgent()
    return _agent

# WebSocket connections
active_connections: List[WebSocket] = []

# ═══════════════════════════════════════════════════════════════════════════════
# MODELY
# ═══════════════════════════════════════════════════════════════════════════════

class QueryRequest(BaseModel):
    query: str

class AnalysisResponse(BaseModel):
    id: str
    query: str
    status: str
    result: Optional[str]
    plan: Optional[dict]
    thoughts: List[dict]
    created_at: str
    completed_at: Optional[str]

# ═══════════════════════════════════════════════════════════════════════════════
# REST ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    return {
        "name": "Gender & Climate Intelligence Hub",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "data_sources": "/api/sources",
            "countries": "/api/countries",
            "analyze": "POST /api/analyze",
            "history": "/api/history",
            "websocket": "WS /ws/analyze"
        }
    }

@app.get("/api/sources")
async def get_data_sources():
    """Seznam všech datových zdrojů"""
    return hub.get_all_sources()

@app.get("/api/countries")
async def get_countries():
    """Seznam všech zemí"""
    return [
        {
            "code": code,
            "name": data["name"],
            "name_en": data["name_en"],
            "region": data["region"],
            "income": data["income"],
            "population": data["population"]
        }
        for code, data in COUNTRIES.items()
    ]

@app.get("/api/country/{country_code}")
async def get_country_profile(country_code: str):
    """Profil země ze všech zdrojů"""
    country_code = country_code.upper()
    if country_code not in COUNTRIES:
        raise HTTPException(status_code=404, detail="Country not found")

    return {
        "country": COUNTRIES[country_code],
        "data": hub.get_country_profile(country_code)
    }

@app.post("/api/analyze")
async def analyze(request: QueryRequest):
    """Spustí analýzu (synchronní)"""
    try:
        analysis = get_agent().run(request.query)
        return analysis.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history():
    """Historie všech analýz"""
    return get_agent().get_history()

@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Konkrétní analýza"""
    analysis = get_agent().get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

@app.delete("/api/history")
async def clear_history():
    """Smazat historii"""
    get_agent().analyses.clear()
    return {"status": "History cleared"}

# ═══════════════════════════════════════════════════════════════════════════════
# WEBSOCKET PRO REAL-TIME STREAMING
# ═══════════════════════════════════════════════════════════════════════════════

@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    """WebSocket pro real-time streaming chain of thought"""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # Přijmout dotaz
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "query":
                query = message.get("query", "")

                # Callback pro streaming thoughts
                async def send_thought(thought: ThoughtStep):
                    await websocket.send_json({
                        "type": "thought",
                        "data": thought.to_dict()
                    })

                # Wrapper pro async callback - potřebujeme thread-safe způsob
                loop = asyncio.get_running_loop()
                def sync_callback(thought):
                    asyncio.run_coroutine_threadsafe(send_thought(thought), loop)

                # Oznámit začátek
                await websocket.send_json({
                    "type": "start",
                    "query": query,
                    "timestamp": datetime.now().isoformat()
                })

                # Spustit analýzu v threadu (agent je sync)
                analysis = await loop.run_in_executor(
                    None,
                    lambda: get_agent().run(query, on_thought=sync_callback)
                )

                # Odeslat výsledek
                await websocket.send_json({
                    "type": "complete",
                    "data": analysis.to_dict()
                })

    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })

# ═══════════════════════════════════════════════════════════════════════════════
# DEMO QUERIES
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/demo-queries")
async def get_demo_queries():
    """Ukázkové dotazy"""
    return [
        {
            "id": 1,
            "query": "Analyzuj genderově-klimatickou situaci v Keni a porovnej ji se Švédskem.",
            "category": "comparison"
        },
        {
            "id": 2,
            "query": "Proveď křížovou analýzu vztahu klimatické zranitelnosti a genderové nerovnosti v Africe.",
            "category": "cross_reference"
        },
        {
            "id": 3,
            "query": "Vypočítej korelaci mezi HDI a gender climate score pro všechny země.",
            "category": "computation"
        },
        {
            "id": 4,
            "query": "Vytvoř policy brief pro Indonésii s konkrétními doporučeními.",
            "category": "policy"
        },
        {
            "id": 5,
            "query": "Které země mají největší mezeru v neplacené péči a jak to souvisí s klimatickou zranitelností?",
            "category": "analysis"
        },
        {
            "id": 6,
            "query": "Jaký je průměrný gender climate score pro země s nízkými příjmy vs vysokými příjmy?",
            "category": "statistics"
        }
    ]

# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "analyses_count": len(_agent.analyses) if _agent else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
