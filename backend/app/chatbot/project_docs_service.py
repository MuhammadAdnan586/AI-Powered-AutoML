"""
AI Project Docs Assistant
--------------------------
RAG-powered chat assistant jo user ke sawalon ka jawab AAPKE
AutoML PROJECT ki documentation (README + code docstrings) se
deta hai — DatasetChatAssistant ki tarah, lekin dataset ki bajaye
poore project ke knowledge base se.

Farq DatasetChatAssistant se:
  - DatasetChatAssistant: poori dataset summary HAMESHA prompt mein
    daal deta hai (chota hota hai, is liye chalta hai)
  - ProjectDocsAssistant: RAG use karta hai — har sawal par sirf
    RELEVANT chunks retrieve karta hai Vector Database se, taake
    poori documentation baar baar na bhejni pare
"""

import os
from pathlib import Path
from typing import List, Dict

import chromadb
import google.generativeai as genai
from dotenv import load_dotenv

# Project root ki .env file load karo (chatbot -> app -> backend -> root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(dotenv_path=_PROJECT_ROOT / ".env")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

CHROMA_DB_PATH = str(
    Path(__file__).resolve().parent.parent.parent / "data" / "project_knowledge_base"
)
COLLECTION_NAME = "project_docs"
TOP_K = 6  # kitne chunks retrieve karne hain har query par


class ProjectDocsAssistant:
    """
    AI assistant jo project ki documentation (README + docstrings)
    se, RAG (Retrieval-Augmented Generation) ke through, sawalon ka
    jawab deta hai.
    """

    def __init__(self):
        self._collection = self._load_collection()
        self.conversation_history: List[Dict] = []
        self.model = genai.GenerativeModel(model_name="gemini-2.5-flash")

    # ------------------------------------------------------------------
    # Vector Database Load Karna
    # ------------------------------------------------------------------
    def _load_collection(self):
        if not os.path.exists(CHROMA_DB_PATH):
            raise RuntimeError(
                "Knowledge base nahi mili. Pehle 'knowledge_base_builder.py' "
                "chalao taake project docs index ho sakein."
            )
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        return client.get_collection(name=COLLECTION_NAME)

    # ------------------------------------------------------------------
    # STEP 1: Retrieval — query se related chunks dhoondna
    # ------------------------------------------------------------------
    def _retrieve_context(self, query: str, top_k: int = TOP_K) -> List[Dict]:
        results = self._collection.query(query_texts=[query], n_results=top_k)
        chunks = []
        for doc, meta, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunks.append({"text": doc, "metadata": meta, "distance": distance})
        return chunks

    # ------------------------------------------------------------------
    # STEP 2: Prompt Banana — Faithfulness Ke Sath
    # ------------------------------------------------------------------
    def _build_prompt(self, user_question: str, retrieved_chunks: List[Dict]) -> str:
        context_text = "\n\n".join(
            f"[Source: {c['metadata'].get('file', 'unknown')}]\n{c['text']}"
            for c in retrieved_chunks
        )

        return f"""Tum AI-Powered-AutoML project ke liye ek helpful documentation
assistant ho. Neeche project ki documentation se retrieve kiye gaye
RELEVANT sections diye gaye hain.

RULES (Faithfulness — zaroori hai follow karna):
- SIRF neeche diye gaye CONTEXT ke basis par jawab do
- Agar context mein jawab nahi hai, saaf keh do: "Ye information
  mujhe available documentation mein nahi mili"
- Apni taraf se koi feature, detail, ya assumption MAT add karo
- Jawab clear aur seedha do, technical jargon zyada mat use karo

=== RETRIEVED CONTEXT ===
{context_text}
==========================

User ka sawal: {user_question}
"""

    # ------------------------------------------------------------------
    # STEP 3: Chat — Retrieval + Generation Dono Ek Saath
    # ------------------------------------------------------------------
    def chat(self, user_message: str) -> Dict:
        retrieved_chunks = self._retrieve_context(user_message)
        prompt = self._build_prompt(user_message, retrieved_chunks)

        response = self.model.generate_content(prompt)
        assistant_message = response.text

        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": assistant_message})

        return {
            "answer": assistant_message,
            "sources": [
                {"file": c["metadata"].get("file"), "type": c["metadata"].get("source_type")}
                for c in retrieved_chunks
            ],
        }

    def reset_conversation(self):
        self.conversation_history = []

    def get_conversation_history(self) -> List[Dict]:
        return self.conversation_history.copy()
