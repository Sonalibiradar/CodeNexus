import os
import json
from fastapi import APIRouter, HTTPException, Query, Body
from sse_starlette.sse import EventSourceResponse
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from ..parsers.scanner import scan_repository
from ..parsers.factory import parser_factory
from ..parsers.models import FileMetadata
from ..graph.builder import CodeKnowledgeGraph
from ..graph.analyzer import GraphAnalyzer
from ..indexing.chunker import ASTChunker
from ..indexing.vector_store import HybridVectorStore
from ..agent.reasoning import CodeNexusAgent
from ..core.config import settings

router = APIRouter()

# Global state in memory for fast local response
state: Dict[str, Any] = {
    "repo_path": "",
    "file_metas": [],
    "ckg": CodeKnowledgeGraph(),
    "store": HybridVectorStore(cache_dir=settings.CACHE_DIR),
    "analyzer": None,
    "agent": None,
    "is_indexed": False
}

class ScanRequest(BaseModel):
    repo_path: str

class AskRequest(BaseModel):
    query: str

@router.get("/status")
async def get_status():
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "active_repo": state["repo_path"],
        "scanned_files_count": len(state["file_metas"]),
        "is_indexed": state["is_indexed"],
        "has_gemini_key": bool(settings.GEMINI_API_KEY)
    }

@router.post("/scan")
async def scan_repo(req: ScanRequest):
    path = os.path.abspath(req.repo_path)
    if not os.path.isdir(path):
        raise HTTPException(status_code=400, detail=f"Directory does not exist: {path}")

    try:
        # Step 1: Scan filesystem
        file_metas = scan_repository(path, max_file_size=settings.MAX_FILE_SIZE_BYTES)
        
        # Step 2: Parse ASTs for each file
        for meta in file_metas:
            try:
                with open(meta.path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                symbols, imports, calls, routes, exports = parser_factory.parse(meta.language, meta.relative_path, content)
                meta.symbols = symbols
                meta.imports = imports
                meta.calls = calls
                meta.routes = routes
                meta.exports = exports
            except Exception:
                continue

        # Step 3: Build Graph & Analyzer
        ckg = CodeKnowledgeGraph()
        ckg.build_from_metadata(file_metas, path)
        analyzer = GraphAnalyzer(ckg)

        # Update state
        state["repo_path"] = path
        state["file_metas"] = file_metas
        state["ckg"] = ckg
        state["analyzer"] = analyzer
        state["is_indexed"] = False
        state["agent"] = CodeNexusAgent(ckg, state["store"], file_metas)

        metrics = analyzer.compute_all_metrics()

        return {
            "success": True,
            "repo_path": path,
            "total_files": len(file_metas),
            "total_symbols": len(ckg.symbols_map),
            "metrics": metrics,
            "files": [f.model_dump(exclude={"symbols", "imports", "calls"}) for f in file_metas[:50]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/index")
async def index_repository():
    if not state["file_metas"]:
        raise HTTPException(status_code=400, detail="No repository scanned yet. Call /api/scan first.")

    chunker = ASTChunker()
    all_chunks = []
    
    for meta in state["file_metas"]:
        try:
            with open(meta.path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            chunks = chunker.chunk_file(meta, content)
            all_chunks.extend(chunks)
        except Exception:
            continue

    state["store"].index_chunks(all_chunks)
    state["is_indexed"] = True
    state["agent"] = CodeNexusAgent(state["ckg"], state["store"], state["file_metas"])

    return {
        "success": True,
        "indexed_chunks_count": len(all_chunks),
        "message": f"Successfully indexed {len(all_chunks)} AST code chunks into Hybrid Vector Store."
    }

@router.get("/graph")
async def get_graph():
    if not state["ckg"]:
        raise HTTPException(status_code=400, detail="Repository not scanned yet.")
    return state["ckg"].get_react_flow_elements()

@router.get("/metrics")
async def get_metrics():
    if not state["analyzer"]:
        raise HTTPException(status_code=400, detail="Repository not scanned yet.")
    return state["analyzer"].compute_all_metrics()

@router.get("/impact")
async def get_impact(target: str = Query(..., description="File path or symbol name")):
    if not state["analyzer"]:
        raise HTTPException(status_code=400, detail="Repository not scanned yet.")
    return state["analyzer"].compute_blast_radius(target)

@router.get("/file/content")
async def get_file_content(path: str = Query(...)):
    if not state["repo_path"]:
        raise HTTPException(status_code=400, detail="Repository not scanned yet.")
    
    full_path = os.path.join(state["repo_path"], path)
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return {"path": path, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask")
async def ask_question(req: AskRequest):
    if not state["agent"]:
        # Auto-scan if needed or return error
        raise HTTPException(status_code=400, detail="Please scan a repository first before asking questions.")

    async def event_generator():
        async for chunk in state["agent"].stream_answer(req.query):
            yield {"data": json.dumps(chunk)}

    return EventSourceResponse(event_generator())
