from typing import List, Tuple, Dict, Any
from .models import SymbolNode, ImportNode, CallSite
from .python_parser import PythonASTParser
from .ts_js_parser import TypeScriptJSParser

class ParserFactory:
    def __init__(self):
        self.py_parser = PythonASTParser()
        self.ts_js_parser = TypeScriptJSParser()

    def parse(self, language: str, file_path: str, content: str) -> Tuple[List[SymbolNode], List[ImportNode], List[CallSite], List[Dict[str, Any]], List[str]]:
        if language == "python":
            return self.py_parser.parse_file(file_path, content)
        elif language in ("typescript", "javascript"):
            return self.ts_js_parser.parse_file(file_path, content)
        else:
            # Fallback parser for generic languages
            return [], [], [], [], []

parser_factory = ParserFactory()
