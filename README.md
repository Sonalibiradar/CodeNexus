# 🌐 CodeNexus

> **An interactive Codebase Intelligence & Architecture Explorer**
> 
> *Map symbols, trace imports, visualize dependency graphs, simulate impact blast radius, and chat with your code.*

---

## 📖 What is CodeNexus?

When you join a new coding project or open an unfamiliar repository, figuring out how everything connects takes hours of reading code manually.

**CodeNexus solves this problem in 4 simple steps:**
1. **Scans & Parses**: Reads files and extracts functions, classes, and import statements using Python AST.
2. **Builds a Graph**: Connects files and symbols together to show what imports what and who calls what.
3. **Analyzes Architecture**: Calculates central hub files (PageRank), detects circular import loops, and finds unused/dead functions.
4. **Interactive Q&A & Blast Radius**: Answers questions about the codebase with cited sources and shows what parts break if you change a file.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**

---

### Step 1: Start the Backend (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend server
uvicorn app.main:app --reload --port 8000
```

> The backend will be live at: `http://127.0.0.1:8000`  
> Interactive Swagger API docs: `http://127.0.0.1:8000/docs`

---

### Step 2: Start the Frontend (React + Vite)

Open a second terminal window:

```bash
# Navigate to frontend directory
cd frontend

# Install packages
npm install

# Start Vite dev server
npm run dev
```

> Open your browser at: `http://localhost:5173`

---

## 🗂️ How the Project is Structured (Simple & Clear)

```text
CodeNexus/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py         # API endpoints (/scan, /graph, /ask, /impact)
│   │   ├── parsers/
│   │   │   ├── scanner.py        # Walks directories and finds source files
│   │   │   ├── python_parser.py  # Reads Python AST to find functions & classes
│   │   │   ├── ts_js_parser.py   # Reads TypeScript & JS symbols and imports
│   │   │   └── models.py         # Simple data models (File, Symbol, Import)
│   │   ├── graph/
│   │   │   ├── builder.py        # Builds the NetworkX graph of files & symbols
│   │   │   └── analyzer.py       # Detects circular dependencies & blast radius
│   │   ├── indexing/
│   │   │   ├── chunker.py        # Chunks code neatly by function and class
│   │   │   └── vector_store.py   # Hybrid keyword & semantic search engine
│   │   ├── agent/
│   │   │   └── reasoning.py      # AI assistant reasoning and citation checker
│   │   ├── core/
│   │   │   └── config.py         # App settings and environment variables
│   │   └── main.py               # FastAPI entrypoint
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Navbar.tsx           # Top navigation and scan bar
    │   │   ├── OverviewView.tsx     # Stats, PageRank hubs, and file list
    │   │   ├── GraphCanvas.tsx      # Interactive 2D drag-and-zoom node map
    │   │   ├── BlastRadiusView.tsx  # Impact simulator (Low/Moderate/High risk)
    │   │   ├── ChatAssistant.tsx    # Streaming chat with citations
    │   │   ├── MetricsView.tsx      # Circular dependency and dead code detector
    │   │   └── FileViewerModal.tsx  # Code viewer modal with line numbers
    │   ├── types.ts                 # Clean TypeScript interfaces
    │   └── App.tsx                  # Main app shell
    └── package.json
```

---

## ✨ Features Explained Simply

### 1. 📊 Codebase Overview & Hubs
- Scans files and shows total lines of code (LOC), programming languages, and symbol counts.
- Highlights the most important "hub" files using PageRank centrality (the files that everything else depends on).

### 2. 🗺️ Interactive Architecture Map
- Built with **React Flow**.
- Drag, zoom, search, and click on file nodes to inspect symbols and see dependencies in real time.

### 3. 💥 Blast Radius Impact Analyzer
- Before making changes to a file or function, simulate what other files and API routes will be impacted.
- Rates changes from **LOW** to **CRITICAL RISK** based on how many downstream components rely on it.

### 4. 💬 Ask CodeNexus (AI Assistant)
- Ask questions like: *"Where does execution start?"* or *"Explain how the graph builder works"*.
- Streams answers token-by-token with **file citations** you can click to inspect the exact source code.

### 5. 🔍 Health & Insights
- Automatically checks for **Circular Dependency Loops** (File A imports File B which imports File A).
- Flags potential **Dead Code** (uncalled functions with 0 callers).

---

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, NetworkX (Graph analysis), AST / Tree-sitter.
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, React Flow (@xyflow/react), Lucide Icons.
- **AI / Search**: Google Gemini API (optional) + BM25 keyword search engine.

---

## 💡 How to Test It

1. Open `http://localhost:5173`.
2. Paste the path to any folder (e.g. `C:\Users\birad\.gemini\antigravity-ide\scratch\CodeNexus\backend`).
3. Click **Scan Repo**.
4. Explore the **Architecture Map**, check the **Blast Radius**, and chat in **Ask CodeNexus**!
