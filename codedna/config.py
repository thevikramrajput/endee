"""
CodeDNA Configuration
=====================
Central configuration for the CodeDNA codebase genome analyzer.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Endee Configuration ────────────────────────────────────────────
ENDEE_HOST = os.getenv("ENDEE_HOST", "localhost")
ENDEE_PORT = int(os.getenv("ENDEE_PORT", "8080"))
ENDEE_AUTH_TOKEN = os.getenv("ENDEE_AUTH_TOKEN", "")
ENDEE_BASE_URL = f"http://{ENDEE_HOST}:{ENDEE_PORT}/api/v1"

# ─── Index Configuration ────────────────────────────────────────────
# Dense index for function-level code embeddings
DENSE_INDEX_NAME = "code_functions"
DENSE_DIMENSION = 384  # all-MiniLM-L6-v2 / CodeBERT dimension
DENSE_SPACE_TYPE = "cosine"

# Hybrid index for combined semantic + keyword search
HYBRID_INDEX_NAME = "code_hybrid"
HYBRID_DENSE_DIM = 384
HYBRID_SPARSE_DIM = 30000  # Vocabulary size for TF-IDF

# Anti-pattern reference index
ANTIPATTERN_INDEX_NAME = "anti_patterns"
ANTIPATTERN_DIMENSION = 384

# ─── Embedding Model Configuration ──────────────────────────────────
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)
CODE_EMBEDDING_MODEL = os.getenv(
    "CODE_EMBEDDING_MODEL", "microsoft/codebert-base"
)
MAX_SEQUENCE_LENGTH = 512

# ─── Parser Configuration ───────────────────────────────────────────
SUPPORTED_LANGUAGES = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "javascript",
    ".tsx": "javascript",
    ".java": "java",
}

# Minimum lines of code for a function to be indexed
MIN_FUNCTION_LOC = 3
MAX_FUNCTION_LOC = 500

# ─── Code Health Configuration ───────────────────────────────────────
# Threshold for anti-pattern similarity (0-1, higher = more similar)
ANTIPATTERN_SIMILARITY_THRESHOLD = 0.80
HEALTH_SCORE_WEIGHTS = {
    "complexity": 0.3,
    "pattern_violations": 0.35,
    "code_duplication": 0.2,
    "documentation": 0.15,
}

# ─── Application Configuration ──────────────────────────────────────
APP_NAME = "CodeDNA"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI-Powered Codebase Genome Analyzer"
BATCH_SIZE = 500  # Vectors to upsert per batch (Optimized for speed)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ─── Paths ──────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATTERNS_DIR = os.path.join(BASE_DIR, "patterns")
CACHE_DIR = os.path.join(BASE_DIR, ".cache")
os.makedirs(CACHE_DIR, exist_ok=True)
