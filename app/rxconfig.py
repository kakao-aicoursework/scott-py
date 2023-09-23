import os
import reflex as rx
from dotenv import load_dotenv

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(PROJECT_DIR, ".env"))


class AppConfig(rx.Config):
    # default
    DEFAULT_OPENAI_MAX_TOKENS: int = 2000
    DEFAULT_OPENAI_TEMPERATURE: float = 0.9
    DEFAULT_OPENAI_MODEL: str = "gpt-3.5-turbo-16k"

    # chroma
    CHROMA_PERSIST_DIRECTORY: str = f"{PROJECT_DIR}/chroma"
    CHROMA_COLLECTION_NAME: str = "project"

    # llm temparature
    LLM_TEMPERATURE: dict[str, float] = {
        "hello": 0.9,
        "bug_request": 0.9,
        "bug_sorry": 0.9,
        "enhancement": 0.9,
        "intent": 0.5,
        "default": 0.9,
        "summarize": 0.1,
        "branch": 0.5,
    }


config = AppConfig(
    app_name="app",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
)
