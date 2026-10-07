import os
import hashlib
from typing import List
import pathspec
from .models import FileMetadata

# Default folders and files to ignore during repository scanning
DEFAULT_IGNORES = [
    ".git", ".svn", ".hg",
    "node_modules", "bower_components",
    "venv", ".venv", "env", ".env", "virtualenv",
    "__pycache__", "*.pyc", "*.pyo", "*.pyd",
    "dist", "build", "target", "out", ".next", ".nuxt", ".output",
    ".idea", ".vscode", ".DS_Store", "Thumbs.db",
    "coverage", ".pytest_cache", ".ruff_cache", ".mypy_cache",
    "*.min.js", "*.min.css", "*.map", "*.bundle.js",
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock"
]

LANGUAGE_EXTENSIONS = {
    ".py": ("python", "source"),
    ".pyi": ("python", "source"),
    ".ts": ("typescript", "source"),
    ".tsx": ("typescript", "source"),
    ".js": ("javascript", "source"),
    ".jsx": ("javascript", "source"),
    ".mjs": ("javascript", "source"),
    ".cjs": ("javascript", "source"),
    ".go": ("go", "source"),
    ".rs": ("rust", "source"),
    ".java": ("java", "source"),
    ".c": ("c", "source"),
    ".cpp": ("cpp", "source"),
    ".h": ("c", "source"),
    ".hpp": ("cpp", "source"),
    ".md": ("markdown", "docs"),
    ".mdx": ("markdown", "docs"),
    ".rst": ("restructuredtext", "docs"),
    ".txt": ("text", "docs"),
    ".json": ("json", "config"),
    ".yaml": ("yaml", "config"),
    ".yml": ("yaml", "config"),
    ".toml": ("toml", "config"),
    ".ini": ("ini", "config"),
    ".xml": ("xml", "config"),
    ".html": ("html", "source"),
    ".css": ("css", "source"),
    ".scss": ("scss", "source"),
    ".sql": ("sql", "data"),
    ".sh": ("shell", "source"),
    ".bash": ("shell", "source"),
    ".ps1": ("powershell", "source"),
    ".dockerfile": ("dockerfile", "config"),
    "dockerfile": ("dockerfile", "config"),
}

def is_test_file(rel_path: str, filename: str) -> bool:
    lowered = rel_path.lower().replace("\\", "/")
    if "test" in lowered or "spec" in lowered or "tests" in lowered:
        return True
    if filename.startswith("test_") or filename.endswith(("_test.py", ".test.ts", ".spec.ts", ".test.js", ".spec.js", "_test.go")):
        return True
    return False

def build_path_spec(root_path: str) -> pathspec.PathSpec:
    patterns = list(DEFAULT_IGNORES)
    gitignore_path = os.path.join(root_path, ".gitignore")
    if os.path.isfile(gitignore_path):
        try:
            with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
                patterns.extend(f.readlines())
        except Exception:
            pass
    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)

def scan_repository(repo_path: str, max_file_size: int = 1024 * 1024) -> List[FileMetadata]:
    repo_path = os.path.abspath(repo_path)
    if not os.path.isdir(repo_path):
        raise ValueError(f"Directory not found: {repo_path}")

    spec = build_path_spec(repo_path)
    file_metas: List[FileMetadata] = []

    for root, dirs, files in os.walk(repo_path):
        rel_root = os.path.relpath(root, repo_path)
        if rel_root == ".":
            rel_root = ""

        # Filter out ignored directories in-place for performance
        dirs[:] = [
            d for d in dirs
            if not spec.match_file(os.path.join(rel_root, d).replace("\\", "/") if rel_root else d)
            and not d.startswith(".")
            and d not in DEFAULT_IGNORES
        ]

        for file in files:
            rel_path = os.path.join(rel_root, file).replace("\\", "/") if rel_root else file
            if spec.match_file(rel_path):
                continue

            full_path = os.path.join(root, file)
            try:
                stat = os.stat(full_path)
                size_bytes = stat.st_size
                if size_bytes > max_file_size or size_bytes == 0:
                    continue

                # Extension & Language
                base_name, ext = os.path.splitext(file.lower())
                if not ext and file.lower() == "dockerfile":
                    lang, cat = "dockerfile", "config"
                else:
                    lang, cat = LANGUAGE_EXTENSIONS.get(ext, ("unknown", "other"))

                # Test file detection
                if is_test_file(rel_path, file):
                    cat = "test"

                # Read and hash
                with open(full_path, "rb") as f:
                    content_bytes = f.read()

                content_hash = hashlib.sha256(content_bytes).hexdigest()
                try:
                    text_content = content_bytes.decode("utf-8")
                    loc = len(text_content.splitlines())
                except UnicodeDecodeError:
                    # Binary or non-UTF8 file
                    continue

                meta = FileMetadata(
                    path=os.path.abspath(full_path).replace("\\", "/"),
                    relative_path=rel_path,
                    extension=ext,
                    language=lang,
                    category=cat,
                    size_bytes=size_bytes,
                    loc=loc,
                    content_hash=content_hash,
                )
                file_metas.append(meta)

            except Exception:
                continue

    return file_metas
