<div align="center">

# 🧬 CodeDNA — AI-Powered Codebase Genome Analyzer

### *Treat your codebase like DNA — analyze its genome, track its evolution, and diagnose its health.*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Endee](https://img.shields.io/badge/Endee-Vector_DB-6C5CE7?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PC9zdmc+&logoColor=white)](https://endee.io)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg?style=for-the-badge)](LICENSE)

<br>

<div align="center">
  <a href="https://codedna-production.up.railway.app/" target="_blank">
    <img src="https://img.shields.io/badge/Live_Demo-🚀_Click_Here_to_Try_CodeDNA-0984E3?style=for-the-badge&logo=rocket" alt="Live Demo">
  </a>
</div>

<br>
<img src="https://img.shields.io/badge/Semantic_Search-✅-00B894?style=flat-square" alt="Semantic Search">
<img src="https://img.shields.io/badge/Hybrid_Search-✅-6C5CE7?style=flat-square" alt="Hybrid Search">
<img src="https://img.shields.io/badge/Health_Analysis-✅-E17055?style=flat-square" alt="Health Analysis">
<img src="https://img.shields.io/badge/Evolution_Tracking-✅-0984E3?style=flat-square" alt="Evolution Tracking">
<img src="https://img.shields.io/badge/Multi_Language-✅-FDCB6E?style=flat-square" alt="Multi-Language">

</div>

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Problem Statement](#-problem-statement)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [How Endee is Used](#-how-endee-is-used)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Usage Guide](#-usage-guide)
- [Testing](#-testing)
- [Technical Deep Dive](#-technical-deep-dive)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Project Overview

**CodeDNA** is an AI-powered **codebase genome analyzer** that maps source code into high-dimensional vector spaces using the **[Endee vector database](https://github.com/endee-io/endee)**. It treats codebases like biological organisms — analyzing their "DNA" (code structure, patterns, dependencies), diagnosing their "health" (anti-patterns, code smells), and tracking their "evolution" (architectural changes over time).

Unlike simple keyword search tools (grep, GitHub search), CodeDNA understands the **semantic meaning** of code. It can find functionally similar code across different programming languages, detect code that resembles known anti-patterns, and visualize the architectural "genome" of an entire codebase.

### What Makes This Different?

| Traditional Tools | CodeDNA |
|---|---|
| Keyword-based search | **Semantic** search using vector embeddings |
| Single language only | **Cross-language** similarity detection |
| No quality analysis | **AI-powered** health diagnostics |
| Static snapshots | **Evolution tracking** with vector drift |
| Basic text matching | **Hybrid search** (dense + sparse vectors) |

---

## 🧩 Problem Statement

Software developers spend approximately **30% of their time** understanding existing code before they can modify it ([IEEE Study](https://ieeexplore.ieee.org)). Current code search tools rely on exact keyword matching, which fails to capture the *intent* and *semantics* of code. This leads to:

1. **Redundant code** — Developers write new code for problems already solved elsewhere in the codebase
2. **Hidden anti-patterns** — Code smells grow undetected until they cause bugs
3. **Architecture drift** — Codebases slowly degrade without visibility into structural changes
4. **Cross-language blindness** — No way to find similar implementations across different languages

**CodeDNA solves all four problems** by leveraging Endee's high-performance vector search to _understand code by meaning, not by text_.

---

## ✨ Key Features

### 1. 🔍 Multi-Modal Semantic Code Search
Search codebases by meaning using natural language or pasting code snippets.

```
Query: "function that validates email addresses using regex"
→ Finds all email validation functions across Python, JavaScript, and Java
```

**Endee Features Used:** Dense index, cosine similarity, `$eq` filter for language

### 2. 🧪 Hybrid Search (Dense + Sparse)
Combines semantic understanding (dense vectors) with keyword precision (sparse TF-IDF vectors) for the best possible retrieval quality.

```
Query: "async request handler middleware express"
→ Dense: understands "request handler middleware" semantically
→ Sparse: boosts results containing exact keywords "async", "express"
→ Combined: best of both worlds
```

**Endee Features Used:** Hybrid index, `sparse_dim`, combined query mode

### 3. 🏥 Codebase Health Diagnostics
Compares every function in your codebase against a vector database of 10+ known anti-patterns:

| Anti-Pattern | Severity | Detection Method |
|---|---|---|
| God Class | 🔴 High | Vector similarity to known God Class patterns |
| Deep Nesting | 🔴 High | Structural similarity + complexity heuristics |
| Callback Hell | 🔴 High | Pattern matching against callback chains |
| Magic Numbers | 🟡 Low | Similarity to hardcoded value patterns |
| Copy-Paste Code | 🟡 Medium | Cross-function vector similarity |
| Hardcoded Credentials | 🔴 Critical | Pattern detection for secrets |
| ...and more | | |

**Endee Features Used:** Anti-pattern index (FLOAT32 precision), similarity threshold queries

### 4. 📈 Architecture Evolution Tracking
Track how your codebase's vector "genome" changes over time:

- **Centroid Drift** — How much the average code semantics shift between versions
- **Spread Analysis** — Whether code is becoming more diverse or converging
- **Complexity Trends** — Track growing or shrinking complexity
- **Genome Maps** — t-SNE/UMAP 2D projections showing code clusters

**Endee Features Used:** Multiple snapshots, vector comparison, centroid computation

### 5. 🌐 Cross-Language Code Intelligence
Find semantically equivalent code across Python, JavaScript, and Java:

```python
# Python: "sort a list of numbers"
def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(0, len(arr)-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
```

→ Also finds equivalent JavaScript and Java implementations!

**Endee Features Used:** Dense index with `$eq` language filter, cross-language query

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard (UI)                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │  Semantic    │ │   Health    │ │  Evolution  │ │ Settings  │ │
│  │  Search     │ │  Analysis   │ │   Tracker   │ │  & Index  │ │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └─────┬─────┘ │
└─────────┼───────────────┼───────────────┼───────────────┼───────┘
          │               │               │               │
┌─────────▼───────────────▼───────────────▼───────────────▼───────┐
│                 CodeDNA Core Engine (Python)                     │
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐               │
│  │ AST Parser │  │  Embedder  │  │   Sparse     │               │
│  │ (Python,   │  │ (Sentence  │  │  Vector Gen  │               │
│  │  JS, Java) │  │ Transformer│  │  (TF-IDF)    │               │
│  └─────┬──────┘  └─────┬──────┘  └──────┬───────┘               │
│        │               │                │                        │
│  ┌─────▼───────────────▼────────────────▼─────────┐             │
│  │              Indexer (Endee Client)             │             │
│  │  • Dense Index    (FLOAT16, cosine, dim=384)    │             │
│  │  • Hybrid Index   (INT8, dense+sparse)          │             │
│  │  • Anti-Pattern   (FLOAT32, high accuracy)      │             │
│  └─────────────────────┬──────────────────────────┘             │
│                        │                                         │
│  ┌─────────────────────▼──────────────────────────┐             │
│  │         Searcher / Analyzer / Tracker           │             │
│  └────────────────────────────────────────────────┘             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │    Endee    │
                    │   Vector    │
                    │  Database   │
                    │  (Docker)   │
                    │  Port 8080  │
                    └─────────────┘
```

### Data Flow

```
Source Code → AST Parsing → Code Units → Embeddings → Endee Indexes
                                            │
User Query → Query Embedding ──────────────→ Endee Search → Results
                                                    ↑
                         Advanced Filters ($eq, $in, $range)
```

---

## 🔋 How Endee is Used

CodeDNA creates **3 specialized indexes** in Endee, each showcasing different capabilities:

### Index 1: `code_functions` — Dense Index
```python
from endee import Endee, Precision

client = Endee()
client.create_index(
    name="code_functions",
    dimension=384,              # all-MiniLM-L6-v2 embedding dim
    space_type="cosine",        # Cosine similarity for code
    precision=Precision.FLOAT16 # Balance of speed & accuracy
)
```
**Purpose:** Function-level semantic code search
**Precision:** FLOAT16 (good balance)
**Use Case:** "Find all functions that handle user authentication"

### Index 2: `code_hybrid` — Hybrid Index (Dense + Sparse)
```python
client.create_index(
    name="code_hybrid",
    dimension=384,              # Dense vector dimension
    sparse_dim=30000,           # TF-IDF vocabulary size
    space_type="cosine",
    precision=Precision.INT8    # Fastest for hybrid queries
)
```
**Purpose:** Combined semantic + keyword search for best retrieval
**Precision:** INT8 (fastest)
**Use Case:** "Find async middleware for Express.js with error handling"

### Index 3: `anti_patterns` — Pattern Reference Index
```python
client.create_index(
    name="anti_patterns",
    dimension=384,
    space_type="cosine",
    precision=Precision.FLOAT32  # Highest accuracy for pattern matching
)
```
**Purpose:** Code health diagnostics against known anti-patterns
**Precision:** FLOAT32 (highest accuracy)
**Use Case:** "Does this function resemble a God Class pattern?"

### Endee Features Demonstrated

| Feature | How It's Used | File |
|---|---|---|
| Dense Index | Function-level semantic search | `core/indexer.py` |
| Hybrid Index | Dense + sparse combined search | `core/indexer.py` |
| `Precision.FLOAT16` | Balanced precision for code index | `core/indexer.py` |
| `Precision.INT8` | Fast hybrid queries | `core/indexer.py` |
| `Precision.FLOAT32` | High-accuracy anti-pattern matching | `core/indexer.py` |
| `$eq` filter | Filter by language, unit type | `core/searcher.py` |
| `$range` filter | Filter by complexity, LOC range | `core/searcher.py` |
| Bulk upsert | Batch indexing with metadata | `core/indexer.py` |
| Metadata storage | Code unit properties (LOC, complexity) | `core/parser.py` |
| Filter storage | Searchable filter fields | `core/parser.py` |
| Hybrid query | Dense + sparse combined query | `core/searcher.py` |
| Dense-only query | Semantic similarity search | `core/searcher.py` |
| Multiple indexes | 3 indexes for different use cases | `core/indexer.py` |
| Docker deployment | `docker-compose.yml` for Endee | `docker-compose.yml` |
| Python SDK | `pip install endee` | All core modules |

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| **Vector Database** | [Endee](https://github.com/endee-io/endee) | High-performance vector storage & search |
| **Backend** | Python 3.10+ | Core engine and pipeline |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) | Dense vector generation for code |
| **Sparse Vectors** | scikit-learn TF-IDF | Sparse keyword-based vectors |
| **Code Parsing** | Python `ast` module + regex | Multi-language AST extraction |
| **Frontend** | Streamlit | Interactive web dashboard |
| **Visualization** | Plotly, t-SNE/UMAP | Code genome visualization |
| **Containerization** | Docker Compose | Endee deployment |
| **CLI** | Rich, Click | Beautiful terminal output |
| **Testing** | pytest | Comprehensive test suite |

---

## 📁 Project Structure

```
endee/                              # Forked Endee repository (base)
├── codedna/                        # 🧬 CodeDNA project directory
│   ├── docker-compose.yml          # Endee server deployment
│   ├── requirements.txt            # Python dependencies
│   ├── config.py                   # Central configuration
│   ├── .env.example                # Environment variable template
│   │
│   ├── core/                       # 🔧 Core engine modules
│   │   ├── __init__.py
│   │   ├── parser.py               # Multi-language AST parser
│   │   ├── embedder.py             # Dense embedding pipeline
│   │   ├── sparse.py               # Sparse vector generation (TF-IDF)
│   │   ├── indexer.py              # Endee index management & upserting
│   │   ├── searcher.py             # Semantic search engine
│   │   ├── analyzer.py             # Code health diagnostics
│   │   └── evolution.py            # Architecture evolution tracking
│   │
│   ├── patterns/                   # 📊 Anti-pattern database
│   │   └── anti_patterns.json      # 10+ curated code anti-patterns
│   │
│   ├── app/                        # 🖥️ Streamlit dashboard
│   │   └── main.py                 # 5-page interactive web app
│   │
│   ├── scripts/                    # 🔨 CLI tools
│   │   ├── ingest_repo.py          # Repository ingestion pipeline
│   │   └── seed_patterns.py        # Anti-pattern seeding script
│   │
│   └── tests/                      # ✅ Test suite
│       ├── test_parser.py          # Parser tests (Python, JS, Java)
│       └── test_embedder.py        # Embedding & sparse vector tests
│
├── README.md                       # This file
├── docs/                           # Endee documentation
├── src/                            # Endee source code
├── install.sh                      # Endee build script
├── run.sh                          # Endee run script
└── docker-compose.yml              # Endee Docker config
```

---

## 🚀 Setup & Installation

### Prerequisites

| Requirement | Version | Purpose |
|---|---|---|
| Docker & Docker Compose | Latest | Running Endee vector database |
| Python | 3.10+ | Core engine and dashboard |
| Git | Latest | Repository cloning |
| 4GB+ RAM | - | Embedding model loading |

### Step 1: Clone the Forked Repository

```bash
git clone https://github.com/thevikramrajput/endee.git
cd endee
```

### Step 2: Start Endee Vector Database

```bash
cd codedna
docker compose up -d
```

Verify Endee is running:
```bash
curl http://localhost:8080/api/v1/index/list
# Expected: [] (empty list)
```

### Step 3: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
cp .env.example .env
# Edit .env if Endee runs on a different host/port
```

### Step 5: Seed Anti-Patterns Database

```bash
python scripts/seed_patterns.py
```

### Step 6: Ingest a Repository

```bash
# Ingest a GitHub repository
python scripts/ingest_repo.py --repo https://github.com/pallets/flask

# OR ingest a local directory
python scripts/ingest_repo.py --path /path/to/your/project --label v1.0
```

### Step 7: Launch the Dashboard

```bash
streamlit run app/main.py
```

Open your browser to **http://localhost:8501** 🎉

---

## 📖 Usage Guide

### Semantic Code Search

1. Navigate to **🔍 Semantic Search** in the sidebar
2. Choose search mode:
   - **Dense** — Pure semantic search (best for natural language queries)
   - **Hybrid** — Combined dense + sparse (best for mixed queries)
   - **Find Similar** — Paste code to find similar implementations
3. Enter your query and apply filters
4. Click **🚀 Search**

**Example Queries:**
```
"function that reads a CSV file and returns a dataframe"
"authentication middleware with JWT token validation"
"database connection pool with retry logic"
"recursive tree traversal algorithm"
```

### Health Analysis

1. Navigate to **🏥 Health Analysis**
2. Enter the path to a local repository
3. Click **🔬 Analyze Codebase**
4. Review:
   - Overall health score (0-100) and letter grade
   - Violation breakdown by severity
   - Individual violation details with suggestions

### Evolution Tracking

1. Navigate to **📈 Evolution**
2. Enter a repository path
3. Click **🧬 Generate Evolution Map**
4. Explore:
   - 2D genome map (t-SNE projection of code vectors)
   - Language distribution pie chart
   - Code unit type histogram

### CLI Usage

```bash
# Full ingestion with health analysis
python scripts/ingest_repo.py --repo https://github.com/user/repo --label v2.0

# Skip health analysis (faster)
python scripts/ingest_repo.py --path ./my-project --no-health

# Seed anti-patterns only
python scripts/seed_patterns.py
```

---

## 🧪 Testing

Run the test suite:

```bash
cd codedna

# Run all tests
pytest tests/ -v

# Run specific test modules
pytest tests/test_parser.py -v
pytest tests/test_embedder.py -v

# Run with coverage
pytest tests/ -v --cov=core --cov-report=html
```

### Test Coverage

| Module | Tests | Coverage Areas |
|---|---|---|
| `parser.py` | 10+ tests | Python/JS/Java parsing, metadata, edge cases |
| `embedder.py` | 5+ tests | Dimension checks, batch embedding, similarity |
| `sparse.py` | 3+ tests | TF-IDF generation, hash-based fallback, tokenization |

---

## 🔬 Technical Deep Dive

### Embedding Pipeline

```
Raw Code → Code Tokenization → Rich Text Preparation → Sentence Transformer → 384-dim Vector
```

The embedder creates a **rich text representation** combining:
1. Unit type and name ("function: calculate_fibonacci")
2. Language context ("language: python")
3. Docstring ("description: Calculate the nth Fibonacci number")
4. Parameters ("parameters: n")
5. Actual code body (truncated to 2048 chars)

This approach ensures the embedding captures both **intent** (from name + docstring) and **implementation** (from code), enabling true semantic search.

### Sparse Vector Generation

```
Raw Code → Comment/String Removal → camelCase/snake_case Splitting → TF-IDF → Sparse Vector
```

The custom `CodeTokenizer`:
- Removes comments, string literals, numeric literals
- Splits camelCase (`getUserById` → `get user by id`)
- Splits snake_case (`get_user_by_id` → `get user by id`)
- Preserves programming keywords
- Generates TF-IDF sparse vectors with 30,000 dimensions

### Health Scoring Algorithm

```
Overall Score = (0.35 × pattern_score) + (0.30 × complexity_score) +
                (0.15 × documentation_score) + (0.20 × duplication_score)
```

| Grade | Score Range |
|---|---|
| A | 90-100 |
| B | 80-89 |
| C | 70-79 |
| D | 60-69 |
| F | 0-59 |

---

## 🔮 Future Enhancements

- [ ] **Real-time Git Hook Integration** — Auto-index on every commit
- [ ] **LLM-Powered Code Explanations** — Use GPT-4/Ollama to explain search results
- [ ] **Code Transplant Recommendations** — Suggest open-source solutions for similar problems
- [ ] **Dependency Graph Visualization** — Network graph of code dependencies
- [ ] **CI/CD Integration** — Health score as a CI quality gate
- [ ] **VSCode Extension** — Semantic search directly from your editor
- [ ] **Multi-Repository Analysis** — Compare codebases across repos

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is built on top of the [Endee](https://github.com/endee-io/endee) vector database, which is licensed under the Apache License 2.0.

The CodeDNA application code is also available under the Apache License 2.0. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [**Endee.io**](https://endee.io) — High-performance vector database powering CodeDNA
- [**Sentence Transformers**](https://www.sbert.net/) — State-of-the-art text embeddings
- [**Streamlit**](https://streamlit.io) — Rapid web app framework
- [**Plotly**](https://plotly.com) — Interactive visualization library

---

<div align="center">

**Built with 🧬&❤️ by CodeDNA Team | Powered by [Endee](https://endee.io)**

</div>
