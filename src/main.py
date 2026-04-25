import os
import asyncio
from pydantic_settings import BaseSettings
from langchain_community.llms import Ollama

class Settings(BaseSettings):
    ENV_MODE: str = os.getenv("ENV_MODE", "local-exe")
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3")

settings = Settings()

async def main():
    print(f"--- Job Agent v1.1.0 (Open Source) ---")
    print(f"Mode: {settings.ENV_MODE} | Model: {settings.LLM_MODEL}")
    # The Ollama connection logic
    llm = Ollama(base_url=settings.OLLAMA_HOST, model=settings.LLM_MODEL)
    print("Ready to process jobs...")

if __name__ == "__main__":
    asyncio.run(main())