import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# .env file load karo
load_dotenv(dotenv_path=Path(".") / ".env")

sys.path.insert(0, "backend")

from app.chatbot.project_docs_service import ProjectDocsAssistant

# Confirm karo key mil gayi
if not os.getenv("GEMINI_API_KEY"):
    print("⚠️  GEMINI_API_KEY nahi mili — .env file check karo")
else:
    print("✅ API Key mil gayi")

assistant = ProjectDocsAssistant()
result = assistant.chat("AutoML SaaS Platform ka overview do — ye kya features offer karta hai?")

print("=" * 50)
print("ANSWER:")
print(result["answer"])
print("\nSOURCES:")
for src in result["sources"]:
    print(f"  - {src}")
print("=" * 50)