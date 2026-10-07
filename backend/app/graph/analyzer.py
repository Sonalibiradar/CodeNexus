import networkx as nx
from typing import Dict, Any, List
from .builder import CodeKnowledgeGraph

class GraphAnalyzer:
    """Computes architectural metrics, circular dependencies, PageRank, and Blast Radius."""

    def __init__(self, ckg: CodeKnowledgeGraph):
        self.ckg = ckg

    def compute_all_metrics(self) -> Dict[str, Any]:
        file_subgraph = self._get_file_subgraph()
        
        # 1. PageRank (Centrality)
        pagerank_scores = {}
        if len(file_subgraph) > 0:
            try:
                pagerank_scores = nx.pagerank(file_subgraph, alpha=0.85)
            except Exception:
                pagerank_scores = {n: 1.0 / len(file_subgraph) for n in file_subgraph.nodes}

        # 2. Circular Dependencies (SCCs)
        cycles = []
        if len(file_subgraph) > 0:
            sccs = list(nx.strongly_connected_components(file_subgraph))
            for scc in sccs:
                if len(scc) > 1:
                    cycles.append(list(scc))

        # 3. Fan-in (Incoming) and Fan-out (Outgoing)
        fan_in = {n: file_subgraph.in_degree(n) for n in file_subgraph.nodes}
        fan_out = {n: file_subgraph.out_degree(n) for n in file_subgraph.nodes}

        # 4. Roots, Leaves, and Isolated files
        roots = [n for n, deg in fan_in.items() if deg == 0 and fan_out.get(n, 0) > 0]
        leaves = [n for n, deg in fan_out.items() if deg == 0 and fan_in.get(n, 0) > 0]
        isolated = [n for n in file_subgraph.nodes if fan_in.get(n, 0) == 0 and fan_out.get(n, 0) == 0]

        # 5. Dead Code Detection
        dead_symbols = self._detect_dead_symbols()

        # 6. Architectural Hubs (Sorted by PageRank)
        top_hubs = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "total_files": len(file_subgraph.nodes),
            "total_import_edges": len(file_subgraph.edges),
            "density": round(nx.density(file_subgraph), 4) if len(file_subgraph) > 0 else 0.0,
            "cycles": cycles,
            "cycles_count": len(cycles),
            "top_hubs": [{"file": k, "score": round(v, 4)} for k, v in top_hubs],
            "roots": roots,
            "leaves": leaves,
            "isolated": isolated,
            "dead_symbols": dead_symbols,
            "dead_symbols_count": len(dead_symbols),
        }

    def compute_blast_radius(self, target_path_or_symbol: str) -> Dict[str, Any]:
        """Calculates all upstream files, symbols, and endpoints affected by modifying a target."""
        g = self.ckg.g
        
        # Check if exact node exists
        matched_node = None
        for n in g.nodes:
            if n == target_path_or_symbol or n.endswith(f"::{target_path_or_symbol}") or n.endswith(f"/{target_path_or_symbol}"):
                matched_node = n
                break

        if not matched_node:
            return {
                "target": target_path_or_symbol,
                "found": False,
                "impacted_files": [],
                "impacted_symbols": [],
                "impacted_endpoints": [],
                "total_impacted": 0,
                "risk_level": "UNKNOWN"
            }

        # Traverse reverse graph
        rg = g.reverse(copy=True)
        try:
            descendants = nx.descendants(rg, matched_node)
        except Exception:
            descendants = set()

        impacted_files = []
        impacted_symbols = []
        impacted_endpoints = []

        for d in descendants:
            data = g.nodes.get(d, {})
            ntype = data.get("node_type")
            if ntype == "file":
                impacted_files.append(d)
            elif ntype == "symbol":
                impacted_symbols.append(d)
            elif ntype == "endpoint":
                impacted_endpoints.append(f"{data.get('method', 'GET')} {data.get('path', '/')}")

        total = len(impacted_files) + len(impacted_symbols) + len(impacted_endpoints)
        
        # Risk assessment
        if len(impacted_endpoints) > 2 or total > 15:
            risk = "CRITICAL"
        elif len(impacted_endpoints) > 0 or total > 5:
            risk = "HIGH"
        elif total > 1:
            risk = "MODERATE"
        else:
            risk = "LOW"

        return {
            "target": matched_node,
            "found": True,
            "risk_level": risk,
            "total_impacted": total,
            "impacted_files": impacted_files,
            "impacted_symbols": impacted_symbols,
            "impacted_endpoints": impacted_endpoints
        }

    def _get_file_subgraph(self) -> nx.DiGraph:
        fg = nx.DiGraph()
        for u, v, d in self.ckg.g.edges(data=True):
            if d.get("relation") == "IMPORTS":
                fg.add_edge(u, v)
        for n, d in self.ckg.g.nodes(data=True):
            if d.get("node_type") == "file" and n not in fg:
                fg.add_node(n)
        return fg

    def _detect_dead_symbols(self) -> List[Dict[str, Any]]:
        dead = []
        for n, d in self.ckg.g.nodes(data=True):
            if d.get("node_type") == "symbol" and d.get("kind") in ("function", "method"):
                # Check if it starts with private/test or is uncalled
                in_degree = self.ckg.g.in_degree(n)
                # If only CONTAINS edge comes in (in_degree == 1) and no CALLS edge
                call_in_edges = [u for u, _, ed in self.ckg.g.in_edges(n, data=True) if ed.get("relation") == "CALLS"]
                if len(call_in_edges) == 0 and not d.get("label", "").startswith(("_", "test_")):
                    dead.append({
                        "symbol": d.get("label"),
                        "file": d.get("file"),
                        "lines": f"{d.get('start_line')}-{d.get('end_line')}"
                    })
        return dead[:25]
