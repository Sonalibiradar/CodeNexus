import re
import hashlib
from typing import List, Tuple, Dict, Any, Optional
from .models import SymbolNode, ImportNode, CallSite

class TypeScriptJSParser:
    """Robust TypeScript & JavaScript AST & structural parser."""

    def parse_file(self, file_path: str, content: str) -> Tuple[List[SymbolNode], List[ImportNode], List[CallSite], List[Dict[str, Any]], List[str]]:
        symbols: List[SymbolNode] = []
        imports: List[ImportNode] = []
        calls: List[CallSite] = []
        routes: List[Dict[str, Any]] = []
        exports: List[str] = []

        lines = content.splitlines()

        # 1. Regex patterns for JS/TS constructs
        import_pattern = re.compile(r"import\s+(?:(?:\*\s+as\s+([A-Za-z0-9_]+)|{([^}]+)}|([A-Za-z0-9_]+))\s+from\s+)?['\"]([^'\"]+)['\"]")
        func_pattern = re.compile(r"(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)")
        arrow_pattern = re.compile(r"(?:export\s+)?(?:const|let|var)\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*(?::\s*[^=]+)?\s*=>")
        class_pattern = re.compile(r"(?:export\s+)?class\s+([A-Za-z0-9_]+)(?:\s+extends\s+([A-Za-z0-9_]+))?(?:\s+implements\s+([A-Za-z0-9_,\s]+))?")
        interface_pattern = re.compile(r"(?:export\s+)?interface\s+([A-Za-z0-9_]+)")
        route_pattern = re.compile(r"(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*(?:async\s*)?(?:function\s*|\([^)]*\)\s*=>|([A-Za-z0-9_]+))")

        for i, line in enumerate(lines, start=1):
            line_str = line.strip()

            # Imports
            imp_match = import_pattern.search(line_str)
            if imp_match:
                star_name, bracket_names, default_name, src_path = imp_match.groups()
                imported = []
                if star_name:
                    imported.append(star_name)
                if default_name:
                    imported.append(default_name)
                if bracket_names:
                    imported.extend([b.strip().split(" as ")[0] for b in bracket_names.split(",") if b.strip()])

                is_rel = src_path.startswith(".")
                imports.append(ImportNode(
                    source_module=src_path,
                    imported_symbols=imported,
                    is_relative=is_rel,
                    import_type="first_party" if is_rel else "third_party",
                    line_number=i
                ))

            # Functions
            f_match = func_pattern.search(line_str)
            if f_match:
                name, raw_params = f_match.groups()
                params = [p.strip().split(":")[0] for p in raw_params.split(",") if p.strip()]
                symbols.append(SymbolNode(
                    name=name,
                    kind="function",
                    file_path=file_path,
                    start_line=i,
                    end_line=min(len(lines), i + 20),
                    parameters=params,
                    ast_hash=hashlib.sha256(f"{name}:{i}".encode("utf-8")).hexdigest()
                ))

            # Arrow functions
            a_match = arrow_pattern.search(line_str)
            if a_match:
                name, raw_params = a_match.groups()
                params = [p.strip().split(":")[0] for p in raw_params.split(",") if p.strip()]
                symbols.append(SymbolNode(
                    name=name,
                    kind="function",
                    file_path=file_path,
                    start_line=i,
                    end_line=min(len(lines), i + 20),
                    parameters=params,
                    ast_hash=hashlib.sha256(f"{name}:{i}".encode("utf-8")).hexdigest()
                ))

            # Classes
            c_match = class_pattern.search(line_str)
            if c_match:
                name, extends_cls, implements_ifaces = c_match.groups()
                bases = []
                if extends_cls:
                    bases.append(extends_cls)
                if implements_ifaces:
                    bases.extend([iface.strip() for iface in implements_ifaces.split(",") if iface.strip()])
                symbols.append(SymbolNode(
                    name=name,
                    kind="class",
                    file_path=file_path,
                    start_line=i,
                    end_line=min(len(lines), i + 50),
                    parameters=bases,
                    ast_hash=hashlib.sha256(f"{name}:{i}".encode("utf-8")).hexdigest()
                ))

            # Interfaces
            if_match = interface_pattern.search(line_str)
            if if_match:
                name = if_match.group(1)
                symbols.append(SymbolNode(
                    name=name,
                    kind="interface",
                    file_path=file_path,
                    start_line=i,
                    end_line=min(len(lines), i + 30),
                    ast_hash=hashlib.sha256(f"{name}:{i}".encode("utf-8")).hexdigest()
                ))

            # Express / Next routes
            r_match = route_pattern.search(line_str)
            if r_match:
                method, path, handler = r_match.groups()
                routes.append({
                    "method": method.upper(),
                    "path": path,
                    "handler": handler or "anonymous_handler",
                    "line": i
                })

            # Check for exports
            if line_str.startswith("export "):
                exports.append(line_str)

        return symbols, imports, calls, routes, exports
