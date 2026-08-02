"""
AI Project Docs Assistant
--------------------------
RAG-powered chat assistant jo user ke sawalon ka jawab AAPKE
AutoML PROJECT ki documentation (README + code docstrings) se
deta hai — DatasetChatAssistant ki tarah, lekin dataset ki bajaye
poore project ke knowledge base se.
"""

import os
from pathlib import Path
from typing import List, Dict

import chromadb
import google.generativeai as genai
from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(dotenv_path=_PROJECT_ROOT / ".env")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

CHROMA_DB_PATH = str(
    Path(__file__).resolve().parent.parent.parent / "data" / "project_knowledge_base"
)
COLLECTION_NAME = "project_docs"
TOP_K = 6


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

    def _load_collection(self):
        if not os.path.exists(CHROMA_DB_PATH):
            raise RuntimeError(
                "Knowledge base nahi mili. Pehle 'knowledge_base_builder.py' "
                "chalao taake project docs index ho sakein."
            )
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        return client.get_collection(name=COLLECTION_NAME)

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

    def _build_prompt(self, user_question: str, retrieved_chunks: List[Dict]) -> str:
        context_text = "\n\n".join(
            f"[Source: {c['metadata'].get('file', 'unknown')}]\n{c['text']}"
            for c in retrieved_chunks
        )

        return f"""CRITICAL LANGUAGE RULE — READ THIS FIRST:
You must respond ONLY in English, using the Latin/Roman alphabet (a-z, A-Z).
Do NOT use Hindi, Urdu, Devanagari script, Chinese, Arabic script, or any
other language or script — no matter what language the user's question is
written in. Your entire response must be plain English text only.

You are a helpful documentation assistant for the AI-Powered-AutoML project.
Below are RELEVANT sections retrieved from the project's documentation.

RULES (Faithfulness — must follow):
- Answer ONLY based on the CONTEXT provided below
- If the answer is not in the context, clearly say:
  "This information is not available in the current documentation"
- Do NOT add any feature, detail, or assumption on your own
- Keep the answer clear and direct, avoid excessive technical jargon

=== RETRIEVED CONTEXT ===
{context_text}
==========================

User's question: {user_question}

REMINDER: Respond in English only, using the Latin alphabet.
"""

    def chat(self, user_message: str) -> Dict:
        retrieved_chunks = self._retrieve_context(user_message)
        prompt = self._build_prompt(user_message, retrieved_chunks)

        response = self.model.generate_content(
            prompt,
            generation_config={"temperature": 0.1},
        )
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