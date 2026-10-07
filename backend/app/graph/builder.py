import os
import networkx as nx
from typing import List, Dict, Any, Optional, Set
from ..parsers.models import FileMetadata, SymbolNode, ImportNode, CallSite

class CodeKnowledgeGraph:
    """Multi-layer directed code knowledge graph for architecture and impact analysis."""

    def __init__(self):
        self.g = nx.MultiDiGraph()
        self.files_map: Dict[str, FileMetadata] = {}
        self.symbols_map: Dict[str, SymbolNode] = {}

    def build_from_metadata(self, file_metas: List[FileMetadata], repo_root: str):
        self.g.clear()
        self.files_map = {f.relative_path: f for f in file_metas}
        self.symbols_map.clear()

        # Step 1: Add File Nodes
        for meta in file_metas:
            self.g.add_node(
                meta.relative_path,
                node_type="file",
                language=meta.language,
                category=meta.category,
                loc=meta.loc,
                size_bytes=meta.size_bytes,
                label=os.path.basename(meta.relative_path),
                path=meta.relative_path
            )

            # Step 2: Add Symbol Nodes and CONTAINS edges
            for sym in meta.symbols:
                sym_id = f"{meta.relative_path}::{sym.name}"
                self.symbols_map[sym_id] = sym
                self.g.add_node(
                    sym_id,
                    node_type="symbol",
                    kind=sym.kind,
                    file=meta.relative_path,
                    start_line=sym.start_line,
                    end_line=sym.end_line,
                    docstring=sym.docstring or "",
                    parameters=sym.parameters,
                    label=sym.name
                )
                self.g.add_edge(meta.relative_path, sym_id, relation="CONTAINS")

            # Step 3: Add Endpoint Nodes & ROUTES_TO edges
            for r in meta.routes:
                route_id = f"ROUTE::{r['method']}::{r['path']}"
                self.g.add_node(
                    route_id,
                    node_type="endpoint",
                    method=r["method"],
                    path=r["path"],
                    handler=r["handler"],
                    file=meta.relative_path,
                    label=f"{r['method']} {r['path']}"
                )
                handler_sym_id = f"{meta.relative_path}::{r['handler']}"
                if handler_sym_id in self.symbols_map:
                    self.g.add_edge(route_id, handler_sym_id, relation="ROUTES_TO")
                else:
                    self.g.add_edge(route_id, meta.relative_path, relation="ROUTES_TO")

        # Step 4: Add IMPORTS Edges between Files
        self._resolve_import_edges(file_metas)

        # Step 5: Add CALLS Edges between Symbols
        self._resolve_call_edges(file_metas)

    def _resolve_import_edges(self, file_metas: List[FileMetadata]):
        for meta in file_metas:
            for imp in meta.imports:
                target_file = self._resolve_import_path(meta.relative_path, imp.source_module)
                if target_file and target_file in self.files_map:
                    self.g.add_edge(
                        meta.relative_path,
                        target_file,
                        relation="IMPORTS",
                        symbols=imp.imported_symbols
                    )

    def _resolve_import_path(self, current_file: str, import_src: str) -> Optional[str]:
        current_dir = os.path.dirname(current_file)
        
        # Relative import
        if import_src.startswith("."):
            levels_up = len(import_src) - len(import_src.lstrip("."))
            module_name = import_src.lstrip(".")
            target_dir = current_dir
            for _ in range(levels_up - 1):
                target_dir = os.path.dirname(target_dir)
            
            parts = module_name.split(".") if module_name else []
            candidate_base = os.path.join(target_dir, *parts).replace("\\", "/")
        else:
            parts = import_src.split(".")
            candidate_base = os.path.join(*parts).replace("\\", "/")

        for ext in [".py", ".ts", ".tsx", ".js", ".jsx", "/__init__.py", "/index.ts", "/index.js"]:
            cand = candidate_base + ext
            if cand in self.files_map:
                return cand
        return None

    def _resolve_call_edges(self, file_metas: List[FileMetadata]):
        for meta in file_metas:
            for call in meta.calls:
                caller_id = f"{meta.relative_path}::{call.caller_symbol}"
                # Look for callee in same file or imported files
                callee_found = False
                for target_sym_id in self.symbols_map:
                    if target_sym_id.endswith(f"::{call.callee_name}"):
                        self.g.add_edge(caller_id, target_sym_id, relation="CALLS")
                        callee_found = True
                        break

    def get_react_flow_elements(self, filter_type: str = "all") -> Dict[str, Any]:
        """Generates nodes and edges ready for frontend React Flow visualization."""
        nodes = []
        edges = []

        # Create subgraphs / file level nodes
        file_nodes = [n for n, d in self.g.nodes(data=True) if d.get("node_type") == "file"]
        
        # Calculate grid positions
        cols = 5
        x_spacing = 280
        y_spacing = 160

        for idx, node_id in enumerate(file_nodes):
            data = self.g.nodes[node_id]
            col = idx % cols
            row = idx // cols
            nodes.append({
                "id": node_id,
                "type": "fileNode",
                "position": {"x": col * x_spacing + 50, "y": row * y_spacing + 50},
                "data": {
                    "id": node_id,
                    "label": data.get("label", node_id),
                    "language": data.get("language", "unknown"),
                    "category": data.get("category", "source"),
                    "loc": data.get("loc", 0),
                    "size_bytes": data.get("size_bytes", 0),
                    "symbols_count": sum(1 for _, _, d in self.g.edges(node_id, data=True) if d.get("relation") == "CONTAINS")
                }
            })

        edge_id_counter = 0
        for u, v, data in self.g.edges(data=True):
            if data.get("relation") == "IMPORTS":
                edge_id_counter += 1
                edges.append({
                    "id": f"e-{edge_id_counter}-{u}-{v}",
                    "source": u,
                    "target": v,
                    "animated": True,
                    "type": "smoothstep",
                    "label": "imports",
                    "style": {"stroke": "#6366f1", "strokeWidth": 2}
                })

        return {"nodes": nodes, "edges": edges, "total_nodes": len(nodes), "total_edges": len(edges)}
