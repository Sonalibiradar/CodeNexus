import hashlib
from typing import List, Dict, Any, Optional
from ..parsers.models import FileMetadata, SymbolNode

class CodeChunk:
    def __init__(
        self,
        chunk_id: str,
        file_path: str,
        content: str,
        start_line: int,
        end_line: int,
        chunk_type: str,  # "symbol", "file_header", "doc_section", "block"
        symbol_name: Optional[str] = None,
        language: str = "text"
    ):
        self.chunk_id = chunk_id
        self.file_path = file_path
        self.content = content
        self.start_line = start_line
        self.end_line = end_line
        self.chunk_type = chunk_type
        self.symbol_name = symbol_name
        self.language = language

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "file_path": self.file_path,
            "content": self.content,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "chunk_type": self.chunk_type,
            "symbol_name": self.symbol_name,
            "language": self.language
        }

class ASTChunker:
    """Deterministic chunker preserving AST boundaries and hierarchy."""

    def chunk_file(self, meta: FileMetadata, full_content: str) -> List[CodeChunk]:
        chunks: List[CodeChunk] = []
        lines = full_content.splitlines()

        if not lines:
            return chunks

        # If file has symbols (functions/classes), create AST symbol chunks
        if meta.symbols:
            covered_lines = set()
            for sym in meta.symbols:
                s_line = max(1, sym.start_line)
                e_line = min(len(lines), sym.end_line)
                symbol_content = "\n".join(lines[s_line - 1 : e_line])
                
                # Context header
                header = f"[{meta.relative_path}] > [{sym.kind.upper()}: {sym.name}]\n"
                chunk_text = header + symbol_content
                
                chunk_id = hashlib.sha256(f"{meta.relative_path}:{sym.name}:{s_line}:{e_line}".encode("utf-8")).hexdigest()[:16]
                chunks.append(CodeChunk(
                    chunk_id=chunk_id,
                    file_path=meta.relative_path,
                    content=chunk_text,
                    start_line=s_line,
                    end_line=e_line,
                    chunk_type="symbol",
                    symbol_name=sym.name,
                    language=meta.language
                ))
                for line_num in range(s_line, e_line + 1):
                    covered_lines.add(line_num)

            # Uncovered parts (e.g. file header, imports, top-level scripts)
            if len(covered_lines) < len(lines):
                uncovered_text = "\n".join([line for idx, line in enumerate(lines, 1) if idx not in covered_lines])
                if uncovered_text.strip():
                    chunk_id = hashlib.sha256(f"{meta.relative_path}:header".encode("utf-8")).hexdigest()[:16]
                    chunks.append(CodeChunk(
                        chunk_id=chunk_id,
                        file_path=meta.relative_path,
                        content=f"[{meta.relative_path}] > [MODULE_IMPORTS_AND_CONFIG]\n" + uncovered_text[:2000],
                        start_line=1,
                        end_line=min(len(lines), 50),
                        chunk_type="file_header",
                        language=meta.language
                    ))
        else:
            # Fallback block chunking (e.g. for markdown, config, small files)
            block_size = 60
            for start_idx in range(0, len(lines), block_size):
                end_idx = min(len(lines), start_idx + block_size)
                chunk_text = f"[{meta.relative_path}] (lines {start_idx + 1}-{end_idx})\n" + "\n".join(lines[start_idx:end_idx])
                chunk_id = hashlib.sha256(f"{meta.relative_path}:{start_idx + 1}:{end_idx}".encode("utf-8")).hexdigest()[:16]
                chunks.append(CodeChunk(
                    chunk_id=chunk_id,
                    file_path=meta.relative_path,
                    content=chunk_text,
                    start_line=start_idx + 1,
                    end_line=end_idx,
                    chunk_type="block",
                    language=meta.language
                ))

        return chunks
