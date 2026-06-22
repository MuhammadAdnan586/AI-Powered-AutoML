"""
AI Dataset Chat Assistant
Uses Google Gemini API to answer questions about the user's dataset.
Provides intelligent insights, statistics, and ML recommendations.
"""
import os
import pandas as pd
import numpy as np
from typing import List, Dict
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class DatasetChatAssistant:
    """
    AI-powered chat assistant that understands the dataset context
    and answers user questions intelligently.
    """

    def __init__(self, df: pd.DataFrame, dataset_name: str = "dataset"):
        self.df = df.copy()
        self.dataset_name = dataset_name
        self.conversation_history: List[Dict] = []
        self.dataset_context = self._build_dataset_context()
        self.system_prompt = self._build_system_prompt()
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=self.system_prompt
        )

    def _build_dataset_context(self) -> str:
        """Build a rich textual summary of the dataset for the AI."""
        numeric_cols = self.df.select_dtypes(include=np.number)
        categorical_cols = self.df.select_dtypes(include="object")

        missing = self.df.isnull().sum()
        missing_cols = missing[missing > 0]

        context = f"""
DATASET: {self.dataset_name}
Shape: {self.df.shape[0]} rows x {self.df.shape[1]} columns

COLUMNS ({self.df.shape[1]} total):
{', '.join(self.df.columns.tolist())}

DATA TYPES:
{self.df.dtypes.to_string()}

NUMERIC COLUMNS ({len(numeric_cols.columns)}):
{numeric_cols.describe().round(3).to_string() if not numeric_cols.empty else 'None'}

CATEGORICAL COLUMNS ({len(categorical_cols.columns)}):
"""
        for col in categorical_cols.columns[:5]:
            context += f"\n  {col}: {self.df[col].nunique()} unique values -> {self.df[col].value_counts().head(3).to_dict()}"

        context += f"""

MISSING VALUES:
{missing_cols.to_string() if not missing_cols.empty else 'No missing values'}

DUPLICATE ROWS: {self.df.duplicated().sum()}

SAMPLE DATA (first 3 rows):
{self.df.head(3).to_string()}
"""
        return context

    def _build_system_prompt(self) -> str:
        return f"""You are an expert Data Scientist and ML Engineer assistant.
The user has uploaded a dataset and you have full access to its statistics and structure.
Answer questions about this dataset clearly and helpfully.
Provide actionable ML insights when relevant.

=== DATASET INFORMATION ===
{self.dataset_context}
===========================

Guidelines:
- Be specific and reference actual column names and statistics
- Suggest ML approaches when appropriate
- Point out data quality issues if asked
- Format numbers nicely
- If asked about something not in the dataset context, say so clearly
"""

    def _to_gemini_history(self) -> List[Dict]:
        """Convert internal history format to Gemini's expected format."""
        gemini_history = []
        for msg in self.conversation_history:
            role = "model" if msg["role"] == "assistant" else "user"
            gemini_history.append({"role": role, "parts": [msg["content"]]})
        return gemini_history

    def chat(self, user_message: str) -> str:
        """
        Send a message and get AI response about the dataset.
        Maintains conversation history for multi-turn context.
        """
        history_before = self._to_gemini_history()
        chat_session = self.model.start_chat(history=history_before)
        response = chat_session.send_message(user_message)
        assistant_message = response.text

        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": assistant_message})

        return assistant_message

    def get_quick_insights(self) -> str:
        """Generate automatic dataset insights without user question."""
        prompt = """Analyze this dataset and provide:
1. 3 key observations about the data
2. Top 2 ML tasks this dataset is suitable for
3. Top 2 data quality concerns to address
4. Best model recommendation with reason

Keep it concise and actionable."""
        return self.chat(prompt)

    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []

    def get_conversation_history(self) -> List[Dict]:
        return self.conversation_history.copy()