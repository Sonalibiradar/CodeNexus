import httpx
import json

def test_api():
    client = httpx.Client(base_url="http://127.0.0.1:8000", timeout=30.0)

    # 1. Status
    status = client.get("/api/status").json()
    print("[1] /api/status:", status)
    assert status["status"] == "online"

    # 2. Scan
    scan = client.post("/api/scan", json={"repo_path": "C:/Users/birad/.gemini/antigravity-ide/scratch/CodeNexus/backend"}).json()
    print(f"[2] /api/scan: Found {scan.get('total_files')} files, {scan.get('total_symbols')} AST symbols.")
    assert scan.get("success") is True

    # 3. Index
    index = client.post("/api/index").json()
    print(f"[3] /api/index: {index.get('message')}")
    assert index.get("success") is True

    # 4. Graph
    graph = client.get("/api/graph").json()
    print(f"[4] /api/graph: {graph.get('total_nodes')} nodes, {graph.get('total_edges')} edges.")
    assert graph.get("total_nodes") > 0

    # 5. Metrics
    metrics = client.get("/api/metrics").json()
    print(f"[5] /api/metrics: Hubs={len(metrics.get('top_hubs', []))}, Cycles={metrics.get('cycles_count')}")

    # 6. Blast Radius
    impact = client.get("/api/impact?target=CodeKnowledgeGraph").json()
    print(f"[6] /api/impact: Target={impact.get('target')}, Risk={impact.get('risk_level')}, TotalImpacted={impact.get('total_impacted')}")

    # 7. Ask streaming test
    print("[7] /api/ask streaming query: 'Explain the CodeKnowledgeGraph and analyzer'")
    with client.stream("POST", "/api/ask", json={"query": "Explain the CodeKnowledgeGraph and analyzer"}) as response:
        for line in response.iter_lines():
            if line.startswith("data: "):
                payload = json.loads(line[6:])
                if payload.get("type") == "token":
                    print(payload.get("content"), end="", flush=True)
                elif payload.get("type") == "final":
                    print(f"\n\n[Final Evaluation] Confidence: {payload.get('confidence')}%, Citations: {payload.get('citations')}")

if __name__ == "__main__":
    test_api()
