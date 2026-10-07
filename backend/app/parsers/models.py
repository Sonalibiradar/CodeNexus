from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SymbolNode(BaseModel):
    name: str
    kind: str  # "function", "class", "method", "interface", "struct", "endpoint"
    file_path: str
    start_line: int
    end_line: int
    docstring: Optional[str] = None
    parameters: List[str] = Field(default_factory=list)
    return_type: Optional[str] = None
    enclosing_symbol: Optional[str] = None
    ast_hash: Optional[str] = None

class CallSite(BaseModel):
    caller_symbol: str
    caller_file: str
    callee_name: str
    line_number: int

class ImportNode(BaseModel):
    source_module: str
    imported_symbols: List[str] = Field(default_factory=list)
    is_relative: bool = False
    import_type: str = "first_party"  # "first_party", "third_party", "stdlib"
    line_number: int = 1

class FileMetadata(BaseModel):
    path: str
    relative_path: str
    extension: str
    language: str
    category: str  # "source", "test", "config", "docs", "data", "asset"
    size_bytes: int
    loc: int
    content_hash: str
    symbols: List[SymbolNode] = Field(default_factory=list)
    imports: List[ImportNode] = Field(default_factory=list)
    calls: List[CallSite] = Field(default_factory=list)
    exports: List[str] = Field(default_factory=list)
    routes: List[Dict[str, Any]] = Field(default_factory=list)  # Web routes (method, path, handler)
