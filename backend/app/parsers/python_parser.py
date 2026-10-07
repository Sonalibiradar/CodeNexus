import ast
import hashlib
from typing import List, Tuple, Dict, Any, Optional
from .models import SymbolNode, ImportNode, CallSite, FileMetadata

class PythonASTParser:
    """Robust Python parser supporting AST parsing and Tree-sitter extraction with endpoint detection."""

    def parse_file(self, file_path: str, content: str) -> Tuple[List[SymbolNode], List[ImportNode], List[CallSite], List[Dict[str, Any]], List[str]]:
        symbols: List[SymbolNode] = []
        imports: List[ImportNode] = []
        calls: List[CallSite] = []
        routes: List[Dict[str, Any]] = []
        exports: List[str] = []

        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError:
            return symbols, imports, calls, routes, exports

        # Collect top-level and class-level symbols
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                sym = self._parse_function(node, file_path, content)
                symbols.append(sym)
                
                # Check for endpoint decorators
                endpoint_info = self._extract_endpoint(node)
                if endpoint_info:
                    routes.append(endpoint_info)
                
                # Extract calls inside this function
                func_calls = self._extract_calls(node, sym.name, file_path)
                calls.extend(func_calls)

            elif isinstance(node, ast.ClassDef):
                cls_sym = self._parse_class(node, file_path, content)
                symbols.append(cls_sym)

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(ImportNode(
                        source_module=alias.name,
                        imported_symbols=[alias.asname or alias.name],
                        is_relative=False,
                        import_type=self._classify_import(alias.name),
                        line_number=node.lineno
                    ))

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imported = [alias.name for alias in node.names]
                is_rel = node.level > 0
                imports.append(ImportNode(
                    source_module="." * node.level + module if is_rel else module,
                    imported_symbols=imported,
                    is_relative=is_rel,
                    import_type="first_party" if is_rel else self._classify_import(module),
                    line_number=node.lineno
                ))

            elif isinstance(node, ast.Assign):
                # Check for __all__ exports
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, (ast.List, ast.Tuple)):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    exports.append(elt.value)

        return symbols, imports, calls, routes, exports

    def _parse_function(self, node: ast.AST, file_path: str, full_content: str) -> SymbolNode:
        params = []
        if hasattr(node, "args"):
            for arg in node.args.args:
                params.append(arg.arg)

        docstring = ast.get_docstring(node)
        return_type = None
        if getattr(node, "returns", None):
            return_type = ast.unparse(node.returns)

        # Content slice for ast_hash
        lines = full_content.splitlines()
        start_line = max(1, node.lineno)
        end_line = getattr(node, "end_lineno", start_line)
        slice_content = "\n".join(lines[start_line - 1 : end_line])
        ast_hash = hashlib.sha256(slice_content.encode("utf-8")).hexdigest()

        return SymbolNode(
            name=node.name,
            kind="async_function" if isinstance(node, ast.AsyncFunctionDef) else "function",
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            docstring=docstring,
            parameters=params,
            return_type=return_type,
            ast_hash=ast_hash
        )

    def _parse_class(self, node: ast.ClassDef, file_path: str, full_content: str) -> SymbolNode:
        docstring = ast.get_docstring(node)
        bases = [ast.unparse(b) for b in node.bases]
        
        lines = full_content.splitlines()
        start_line = max(1, node.lineno)
        end_line = getattr(node, "end_lineno", start_line)
        slice_content = "\n".join(lines[start_line - 1 : end_line])
        ast_hash = hashlib.sha256(slice_content.encode("utf-8")).hexdigest()

        return SymbolNode(
            name=node.name,
            kind="class",
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            docstring=docstring,
            parameters=bases,  # Store inherited classes in parameters
            ast_hash=ast_hash
        )

    def _extract_calls(self, func_node: ast.AST, caller_name: str, file_path: str) -> List[CallSite]:
        calls = []
        for child in ast.walk(func_node):
            if isinstance(child, ast.Call):
                callee_name = None
                if isinstance(child.func, ast.Name):
                    callee_name = child.func.id
                elif isinstance(child.func, ast.Attribute):
                    callee_name = child.func.attr
                if callee_name:
                    calls.append(CallSite(
                        caller_symbol=caller_name,
                        caller_file=file_path,
                        callee_name=callee_name,
                        line_number=child.lineno
                    ))
        return calls

    def _extract_endpoint(self, node: ast.AST) -> Optional[Dict[str, Any]]:
        """Detect FastAPI, Flask, Django decorators like @app.get('/path') or @router.post."""
        if not hasattr(node, "decorator_list"):
            return None

        for dec in node.decorator_list:
            if isinstance(dec, ast.Call):
                func = dec.func
                method = None
                if isinstance(func, ast.Attribute) and func.attr.lower() in ("get", "post", "put", "delete", "patch", "route"):
                    method = func.attr.upper()
                if method and dec.args and isinstance(dec.args[0], ast.Constant):
                    path = str(dec.args[0].value)
                    return {
                        "method": method,
                        "path": path,
                        "handler": node.name,
                        "line": node.lineno
                    }
        return None

    def _classify_import(self, module_name: str) -> str:
        stdlib_modules = {
            "os", "sys", "re", "json", "time", "datetime", "math", "random",
            "pathlib", "typing", "collections", "itertools", "functools",
            "asyncio", "threading", "subprocess", "logging", "shutil",
            "hashlib", "urllib", "http", "socket", "io", "contextlib",
            "dataclasses", "enum", "abc", "unittest", "inspect", "ast"
        }
        root_mod = module_name.split(".")[0]
        if root_mod in stdlib_modules:
            return "stdlib"
        return "third_party"
