import os
import pynecone as pc

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY is not None, "OPENAI_API_KEY is not set"


class ChatConfig(pc.Config):
    pass


config = ChatConfig(
    app_name="chat",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)
