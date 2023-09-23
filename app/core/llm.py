import os

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, FileChatMessageHistory
from langchain.prompts import PromptTemplate
from langchain.schema.messages import BaseMessage

from core.chroma import get_similar_docs
from core.prompts import (
    SAY_HELLO,
    BUG_REQUEST_CONTEXT,
    BUG_SAY_SORRY,
    ENHANCEMENT_SAY_THANKS,
    PARSE_INTENT,
    DEFAULT_RESPONSE,
    SUMMARIZE,
    BRANCH
)
from rxconfig import config, PROJECT_DIR

LLM_DICT: dict[str, ChatOpenAI] = {}
CHAIN_DICT: dict[str, LLMChain] = {}
_SUMMARY: dict = {}


def get_or_create_llm(name: str = "default", streaming: bool = False) -> ChatOpenAI:
    """
    llm model을 생성하거나 이미 생성된 llm model을 반환합니다.
    """

    if not LLM_DICT.get(name):
        temperature = config.LLM_TEMPERATURE.get(
            name,
            config.DEFAULT_OPENAI_TEMPERATURE
        )
        options = dict(
            temperature=temperature,
            max_tokens=config.DEFAULT_OPENAI_MAX_TOKENS,
            model=config.DEFAULT_OPENAI_MODEL,
        )
        if streaming:
            options["streaming"] = True
            options["callbacks"] = [StreamingStdOutCallbackHandler()]
        LLM_DICT[name] = ChatOpenAI(**options)
    return LLM_DICT[name]


def get_or_create_chain(
    name: str,
    output_key: str = None,
    template: str = None,
    streaming: bool = False,
    verbose: bool = False,
) -> LLMChain:
    """
    chain을 생성하거나 이미 생성된 chain을 반환합니다.
    """
    if os.getenv("VERBOSE"):
        verbose = True

    if not CHAIN_DICT.get(name):
        if not template:
            raise ValueError("template must be provided if chain does not exist")
        if not output_key:
            output_key = name
        CHAIN_DICT[name] = LLMChain(
            llm=get_or_create_llm(name, streaming=streaming),
            prompt=PromptTemplate.from_template(
                template=template
            ),
            output_key=output_key,
            verbose=verbose
        )
    return CHAIN_DICT[name]


def init_chains():
    """template과 매칭하여 미리 context를 선택합니다."""
    for name, template, streaming in [
        ("hello", SAY_HELLO, True),
        ("bug_request", BUG_REQUEST_CONTEXT, True),
        ("bug_sorry", BUG_SAY_SORRY, True),
        ("enhancement", ENHANCEMENT_SAY_THANKS, True),
        ("default", DEFAULT_RESPONSE, True),
        ("intent", PARSE_INTENT, False),
        ("summarize", SUMMARIZE, False),
        ("branch", BRANCH, False),
    ]:
        get_or_create_chain(name=name, template=template, streaming=streaming)


def load_conversation_history(conversation_id: str) -> FileChatMessageHistory:
    history_path = os.path.join(PROJECT_DIR, "history", f"{conversation_id}.json")
    os.makedirs(os.path.dirname(history_path), exist_ok=True)
    return FileChatMessageHistory(history_path)


def get_history(conversion_id: str) -> list[BaseMessage]:
    history = load_conversation_history(conversation_id=conversion_id)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="user_message",
        chat_memory=history,
    )

    return memory.buffer


def clear_history(conversation_id: str):
    history = load_conversation_history(conversation_id=conversation_id)
    history.clear()


def create_answer(user_message: str, conversation_id: str = None) -> dict:
    """create answer by return"""
    from .preprocess import SUMMARY

    history = load_conversation_history(conversation_id)

    keys = ", ".join(list(SUMMARY.keys()))
    summary = "\n".join([
        f"{key}: {summary.replace('n', ' ')}"
        for key, summary in SUMMARY.items()
    ])

    context = dict(
        user_message=user_message,
        keys=keys,
        summary=summary
    )

    # determine which data_source_context
    branch_chain = get_or_create_chain("branch")
    branch = branch_chain.run(context)

    def get_documents_str():
        return "\n".join(
            get_similar_docs(
                user_message,
                top_k=10,
                filters={
                    "$and": [
                        # restrict to selected data source context
                        {"data_source": branch},
                        # not equal to Title
                        {"category": {"$ne": "Title"}}
                    ],
                }
            )
        )

    # create main context
    context = dict(user_message=user_message)
    context.update(
        user_message=user_message,
        chat_history=get_history(conversation_id),
    )

    # which intent
    intent_chain = get_or_create_chain("intent")
    intent = intent_chain.run(context)

    if intent == "hello":
        context.update(related_documents=get_documents_str())
        answer = get_or_create_chain("hello").run(context)

    elif intent == "bug":
        context.update(related_documents=get_documents_str())

        answer = ""
        for name in ["bug_request", "bug_sorry"]:
            chain = get_or_create_chain(name)
            context = chain(context)
            answer += context[chain.output_key] + "\n\n"

    elif intent == "enhancement":
        chain = get_or_create_chain("enhancement")
        answer = chain.run(context)

    else:
        context.update(related_documents=get_documents_str())
        answer = get_or_create_chain("default").run(context)

    history.add_user_message(user_message)
    history.add_ai_message(answer)
    return {
        "conversation_id": conversation_id,
        "user_message": user_message,
        "branch": branch,
        "intent": intent,
        "answer": answer
    }


def generate_answer(user_message: str, conversation_id: str = None):
    """generate answer by yield"""
    from .preprocess import SUMMARY

    history = load_conversation_history(conversation_id)

    keys = ", ".join(list(SUMMARY.keys()))
    summary = "\n".join([
        f"{key}: {summary.replace('n', ' ')}"
        for key, summary in SUMMARY.items()
    ])

    context = dict(
        user_message=user_message,
        keys=keys,
        summary=summary
    )

    # determine which data_source_context
    branch_chain = get_or_create_chain("branch")
    branch = branch_chain.run(context)

    def get_documents_str():
        return "\n".join(
            get_similar_docs(
                user_message,
                top_k=10,
                filters={
                    "$and": [
                        # restrict to selected data source context
                        {"data_source": branch},
                        # not equal to Title
                        {"category": {"$ne": "Title"}}
                    ],
                }
            )
        )

    # create main context
    context = dict(user_message=user_message)
    context.update(
        user_message=user_message,
        chat_history=get_history(conversation_id),
    )

    # which intent
    intent_chain = get_or_create_chain("intent")
    intent = intent_chain.run(context)

    answer = ""

    if intent == "hello":
        context.update(related_documents=get_documents_str())
        for response in get_or_create_chain("hello").run(context):
            answer += response
            yield response

    elif intent == "bug":
        context.update(related_documents=get_documents_str())

        for response in get_or_create_chain("bug_request").run(context):
            answer += response
            yield response

        answer += "\n\n"
        yield "\n\n"

        for response in get_or_create_chain("bug_sorry").run(context):
            answer += response
            yield response

    elif intent == "enhancement":
        for response in get_or_create_chain("enhancement").run(context):
            answer += response
            yield response

    else:
        context.update(related_documents=get_documents_str())
        for response in get_or_create_chain("default").run(context):
            answer += response
            yield response

    history.add_user_message(user_message)
    history.add_ai_message(answer)
    return {
        "conversation_id": conversation_id,
        "user_message": user_message,
        "branch": branch,
        "intent": intent,
        "answer": answer
    }


init_chains()
