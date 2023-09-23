from .const import *
from .chroma import get_similar_docs, query_db, init_chroma
from .preprocess import load_data_and_upload_chroma
from .llm import init_chains, create_answer, generate_answer

__all__ = [
    "init",
    "query_db",
    "get_similar_docs",
    "create_answer",
    "generate_answer",
]

_INITIALIZED = False


def init():
    global _INITIALIZED
    if not _INITIALIZED:
        init_chroma()
        init_chains()
        load_data_and_upload_chroma()
        _INITIALIZED = True

init()