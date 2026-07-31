"""
Project Knowledge Base Builder
--------------------------------
Ye script poore AI-Powered-AutoML project ko scan karta hai:
  1. Saari README*.md files (project overview, setup instructions)
  2. Har .py file ke andar ke docstrings (module, class, function level)

Har piece ko chhote, meaningful "chunks" mein todta hai (Recursive
Chunking strategy — pehle paragraphs se, phir sentences se todta hai,
taake koi baat beech mein na kate), aur ChromaDB (Vector Database)
mein store kar deta hai, taake baad mein RAG chatbot inhe retrieve
kar sake.

Isay ek dafa chalao jab bhi project ke docs/code update hon:
    python knowledge_base_builder.py
"""

import ast
import os
from pathlib import Path
from typing import List, Dict

import chromadb

# ---------------------------------------------------------------------
# CONFIG — apni project ke hisaab se adjust karo
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # repo ka root folder
FOLDERS_TO_SCAN = [
    "backend/app",
    "explainability",
    "data_quality",
    "model_registry",
]
CHROMA_DB_PATH = str(PROJECT_ROOT / "backend" / "data" / "project_knowledge_base")
COLLECTION_NAME = "project_docs"

CHUNK_SIZE = 600         # har chunk mein max ~600 characters
CHUNK_OVERLAP = 80       # context break na ho, is liye thora overlap


# ---------------------------------------------------------------------
# STEP 1: Recursive Chunking (bina kisi extra library ke, pure Python)
# ---------------------------------------------------------------------

def recursive_split(text: str, chunk_size: int = CHUNK_SIZE,
                     overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Text ko natural boundaries (paragraph -> sentence -> word) se
    todta hai, taake sentences beech mein na katein.
    """
    text = text.strip()
    if len(text) <= chunk_size:
        return [text] if text else []

    separators = ["\n\n", "\n", ". ", " "]

    def split_on(sep: str, s: str) -> List[str]:
        parts = s.split(sep)
        return [p + sep if i < len(parts) - 1 else p for i, p in enumerate(parts)]

    def _split(s: str, sep_index: int) -> List[str]:
        if len(s) <= chunk_size:
            return [s] if s.strip() else []
        if sep_index >= len(separators):
            # aakhri resort: seedha character count se kaato
            return [s[i:i + chunk_size] for i in range(0, len(s), chunk_size)]

        pieces = split_on(separators[sep_index], s)
        chunks, current = [], ""
        for piece in pieces:
            if len(current) + len(piece) <= chunk_size:
                current += piece
            else:
                if current.strip():
                    chunks.extend(_split(current, sep_index + 1) if len(current) > chunk_size
                                  else [current])
                current = piece
        if current.strip():
            chunks.extend(_split(current, sep_index + 1) if len(current) > chunk_size
                          else [current])
        return chunks

    raw_chunks = _split(text, 0)

    # Overlap add karo — har chunk ke shuru mein pichle chunk ka
    # aakhri hissa bhi rakho, taake context na tootay
    final_chunks = []
    for i, chunk in enumerate(raw_chunks):
        if i > 0 and overlap > 0:
            prev_tail = raw_chunks[i - 1][-overlap:]
            chunk = prev_tail + chunk
        final_chunks.append(chunk.strip())

    return [c for c in final_chunks if c]


# ---------------------------------------------------------------------
# STEP 2: README Files Extract Karna
# ---------------------------------------------------------------------

def extract_readme_chunks() -> List[Dict]:
    """Root mein maujood saari README*.md files se chunks banata hai."""
    entries = []
    for readme_path in PROJECT_ROOT.glob("README*.md"):
        try:
            text = readme_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for chunk in recursive_split(text):
            entries.append({
                "text": chunk,
                "metadata": {
                    "source_type": "readme",
                    "file": readme_path.name,
                }
            })
    return entries


# ---------------------------------------------------------------------
# STEP 3: Python Files Se Docstrings Extract Karna
# ---------------------------------------------------------------------

def extract_docstrings_from_file(file_path: Path) -> List[Dict]:
    """
    Ek .py file ke andar se module, class, aur function-level
    docstrings nikalta hai — ye asal 'documentation' hoti hai
    jo code kya karta hai wo batati hai.
    """
    entries = []
    try:
        source = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError, ValueError):
        return entries

    relative_path = file_path.relative_to(PROJECT_ROOT).as_posix()

    # Module-level docstring
    module_doc = ast.get_docstring(tree)
    if module_doc:
        for chunk in recursive_split(module_doc):
            entries.append({
                "text": f"[{relative_path}] Module overview: {chunk}",
                "metadata": {
                    "source_type": "docstring",
                    "file": relative_path,
                    "symbol": "<module>",
                }
            })

    # Class aur Function level docstrings
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node)
            if not doc:
                continue
            kind = "class" if isinstance(node, ast.ClassDef) else "function"
            for chunk in recursive_split(doc):
                entries.append({
                    "text": f"[{relative_path}] {kind} '{node.name}': {chunk}",
                    "metadata": {
                        "source_type": "docstring",
                        "file": relative_path,
                        "symbol": node.name,
                    }
                })
    return entries


def extract_all_code_docs() -> List[Dict]:
    """FOLDERS_TO_SCAN mein har .py file scan karke docstrings nikalta hai."""
    EXCLUDE_MARKERS = {"venv", "site-packages", "__pycache__", ".git", "node_modules"}
    entries = []
    for folder in FOLDERS_TO_SCAN:
        folder_path = PROJECT_ROOT / folder
        if not folder_path.exists():
            continue
        for py_file in folder_path.rglob("*.py"):
            # Agar path mein venv/site-packages waghera aaye to skip karo
            if EXCLUDE_MARKERS & set(py_file.parts):
                continue
            entries.extend(extract_docstrings_from_file(py_file))
    return entries


# ---------------------------------------------------------------------
# STEP 4: Sab Kuch ChromaDB (Vector Database) Mein Store Karna
# ---------------------------------------------------------------------

def build_knowledge_base() -> None:
    print("📚 Documentation collect ki ja rahi hai...")
    readme_chunks = extract_readme_chunks()
    code_chunks = extract_all_code_docs()
    all_chunks = readme_chunks + code_chunks

    if not all_chunks:
        print("⚠️  Koi content nahi mila. FOLDERS_TO_SCAN aur PROJECT_ROOT check karo.")
        return

    print(f"   -> {len(readme_chunks)} README chunks")
    print(f"   -> {len(code_chunks)} code/docstring chunks")
    print(f"   -> Total: {len(all_chunks)} chunks")

    os.makedirs(CHROMA_DB_PATH, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    # Purani collection hai to delete karke fresh banao (re-indexing)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(name=COLLECTION_NAME)

    print("🧠 Embeddings generate ho rahi hain aur Vector DB mein save ho raha hai...")
    batch_size = 100
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        collection.add(
            documents=[c["text"] for c in batch],
            metadatas=[c["metadata"] for c in batch],
            ids=[f"chunk_{i + j}" for j in range(len(batch))],
        )

    print(f"✅ Knowledge base ready hai: {CHROMA_DB_PATH}")


if __name__ == "__main__":
    build_knowledge_base()
