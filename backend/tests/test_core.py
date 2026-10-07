import os
import pytest
from app.parsers.scanner import scan_repository
from app.parsers.factory import parser_factory
from app.graph.builder import CodeKnowledgeGraph
from app.graph.analyzer import GraphAnalyzer
from app.indexing.chunker import ASTChunker
from app.indexing.vector_store import HybridVectorStore

def test_scan_and_parse():
    # Scan the backend directory itself
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = scan_repository(backend_dir)
    assert len(files) > 0

    # Test Python parsing
    py_files = [f for f in files if f.language == "python"]
    assert len(py_files) > 0

    for pf in py_files:
        with open(pf.path, "r", encoding="utf-8") as f:
            content = f.read()
        symbols, imports, calls, routes, exports = parser_factory.parse("python", pf.relative_path, content)
        pf.symbols = symbols
        pf.imports = imports
        pf.calls = calls
        pf.routes = routes

    # Test CKG Build
    ckg = CodeKnowledgeGraph()
    ckg.build_from_metadata(files, backend_dir)
    assert len(ckg.g.nodes) > 0

    # Test Analyzer
    analyzer = GraphAnalyzer(ckg)
    metrics = analyzer.compute_all_metrics()
    assert "total_files" in metrics
    assert "top_hubs" in metrics

    # Test AST Chunking
    chunker = ASTChunker()
    chunks = []
    for pf in py_files[:3]:
        with open(pf.path, "r", encoding="utf-8") as f:
            content = f.read()
        chunks.extend(chunker.chunk_file(pf, content))
    assert len(chunks) > 0

    # Test Vector Store & BM25
    store = HybridVectorStore(cache_dir=".test_cache")
    store.index_chunks(chunks)
    res = store.hybrid_search("CodeKnowledgeGraph", top_k=3)
    assert len(res) > 0
