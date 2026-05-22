import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
RAG_DOCS_DIR = PROJECT_ROOT / "rag" / "docs"
CHROMA_PATH = str(PROJECT_ROOT / "rag" / "chroma_db")
DEMO_DIR = PROJECT_ROOT / "demo"

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
# Override via env var: GEMMA_MODEL=gemma4:e4b python app.py
GEMMA_MODEL = os.environ.get("GEMMA_MODEL", "gemma4:31b")
EMBED_MODEL = "intfloat/multilingual-e5-base"

TOP_K_RETRIEVAL = 3
MIN_CHUNK_SIZE = 200
MAX_CHUNK_SIZE = 800
