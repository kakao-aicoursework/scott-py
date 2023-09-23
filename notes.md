# chromadb

### 1. sample 1

```python
import chromadb

# 다음으로, Chroma DB를 이용하기 위해 Chroma 클라이언트를 생성함
# 이 클라이언트는 Chroma DB 서버와 통신해서, 데이터를 생성, 조회, 수정, 삭제하는 방법을 제공함
client = chromadb.PersistentClient()
# PersistentClient는 데이터를 파일에 저장합니다. 그 외에 메모리에 저장하는 EphmeralClient, 네트워크를 통해서 접속하는 HttpClient가 있음.
# 실제 서비스에서는 HttpClient가 권장됩니다.

# Chroma에서 각각의 데이터를 document라고 함. 이 문서를 그룹핑해서 관리하는 개념이 collection임.
# document를 만들기 전에 collection을 생성해야 함.
posts = client.create_collection(
    name="posts"
)

# 생성한 컬렉션에 텍스트 문서를 추가
post1 = 'apple is delicious'
post2 = 'banana is sweet'
post3 = 'New York is big'
post4 = 'Paris is romantic'

# documents에 document의 내용이 들어가고, ids에 각 문서의 식별자가 들어감.
posts.add(
    documents=[post1, post2, post3, post4],
    ids=["1", "2", "3", "4"]
)

# query_texts의 목록을 제공하면, Chroma DB는 가장 유사한 결과를 반환. n_results는 출력할 결과의 수임.
result = posts.query(
    query_texts=['yellow'],
    n_results=1
)

print(result)
```

endregion

### 2. sample 2

```python
import chromadb

client = chromadb.PersistentClient()

collection = client.get_or_create_collection(
    name="k-drama",
    metadata={"hnsw:space": "cosine"}
)

# 데이터 인덱스
ids = []
# 메타데이터
doc_meta = []
# 벡터로 변환 저장할 텍스트 데이터로 ChromaDB에 Embedding 데이터가 없으면 자동으로 벡터로 변환해서 저장
documents = []

for idx in range(len(filter_df)):
    item = filter_df.iloc[idx]
    id = item['Name'].lower().replace(' ', '-')
    document = f"{item['Name']}: {item['Synopsis']} : {str(item['Cast']).strip().lower()} : {str(item['Genre']).strip().lower()}"
    meta = {
        "rating": item['Rating']
    }

    ids.append(id)
    doc_meta.append(meta)
    documents.append(document)

# DB 저장
collection.add(
    documents=documents,
    metadatas=doc_meta,
    ids=ids
)
# DB 쿼리
collection.query(
    query_texts=["romantic comedy drama"],
    n_results=5,
)

```

endregion

# MultiPromptChain

```bash
pip install openai langchain
```

```python
import os

CUR_DIR = os.path.dirname(os.path.abspath('/content/drive/MyDrive/LLM-Lecture/datas/prompt_template2/'))
BUG_STEP1_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt_template2/bug_say_sorry.txt")
BUG_STEP2_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt_template2/bug_request_context.txt")
ENHANCE_STEP1_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt_template2/enhancement_say_thanks.txt")
INTENT_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt_template2/parse_intent.txt")


def read_prompt_template(file_path: str) -> str:
    with open(file_path, "r") as f:
        prompt_template = f.read()

    return prompt_template


from langchain.chains import ConversationChain, LLMChain, LLMRouterChain
from langchain.chains.router import MultiPromptChain
from langchain.chains.router.llm_router import RouterOutputParser
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import ChatPromptTemplate
from pprint import pprint


def create_chain(llm, template_path, output_key):
    return LLMChain(
        llm=llm,
        prompt=ChatPromptTemplate.from_template(
            template=read_prompt_template(template_path)
        ),
        output_key=output_key,
        verbose=True,
    )


llm = ChatOpenAI(temperature=0.1, max_tokens=200, model="gpt-3.5-turbo")

bug_step1_chain = create_chain(
    llm=llm,
    template_path=BUG_STEP1_PROMPT_TEMPLATE,
    output_key="bug-step1",
)
bug_step2_chain = create_chain(
    llm=llm,
    template_path=BUG_STEP2_PROMPT_TEMPLATE,
    output_key="bug-step2",
)
enhance_step1_chain = create_chain(
    llm=llm,
    template_path=ENHANCE_STEP1_PROMPT_TEMPLATE,
    output_key="enhance-step1",
)
parse_intent_chain = create_chain(
    llm=llm,
    template_path=INTENT_PROMPT_TEMPLATE,
    output_key="intent",
)
default_chain = ConversationChain(llm=llm, output_key="text")

destinations = [
    "bug: Related to a bug, vulnerability, unexpected error with an existing feature",
    "documentation: Changes to documentation and examples, like .md, .rst, .ipynb files. Changes to the docs/ folder",
    "enhancement: A large net-new component, integration, or chain. Use sparingly. The largest features",
    "improvement: Medium size change to existing code to handle new use-cases",
    "nit: Small modifications/deletions, fixes, deps or improvements to existing code or docs",
    "question: A specific question about the codebase, product, project, or how to use a feature",
    "refactor: A large refactor of a feature(s) or restructuring of many files",
]

destinations = "\n".join(destinations)
destinations

router_prompt_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(destinations=destinations)
router_prompt = PromptTemplate.from_template(
    template=router_prompt_template, output_parser=RouterOutputParser()
)
router_chain = LLMRouterChain.from_llm(llm=llm, prompt=router_prompt, verbose=True)

multi_prompt_chain = MultiPromptChain(
    router_chain=router_chain,
    destination_chains={
        "bug": bug_step1_chain,
        "enhancement": enhance_step1_chain,
    },
    default_chain=ConversationChain(llm=llm, output_key="text"),
)

INTENT_LIST_TXT = os.path.join(CUR_DIR, "prompt_template2/intent_list.txt")


def gernerate_answer(user_message) -> dict[str, str]:
    context = dict(user_message=user_message)
    context["input"] = context["user_message"]
    context["intent_list"] = read_prompt_template(INTENT_LIST_TXT)

    # intent = parse_intent_chain(context)["intent"]
    intent = parse_intent_chain.run(context)

    if intent == "bug":
        answer = ""
        for step in [bug_step1_chain, bug_step2_chain]:
            answer += step.run(context)
            answer += "\n\n"
    elif intent == "enhancement":
        answer = enhance_step1_chain.run(context)
    else:
        answer = default_chain.run(context)

    return {"answer": answer}


gernerate_answer('i have a bug')
gernerate_answer('나는 현재 버그 문제가 있어')
gernerate_answer('i have a good idea')
```

endregion

# upload chroma

```python
import os

DATA_DIR = os.path.dirname(os.path.abspath('/content/drive/MyDrive/datas/upload/'))

SK_CODE_DIR = os.path.join(DATA_DIR, "upload/codes", "python")
SK_SAMPLE_DIR = os.path.join(DATA_DIR, "upload/codes", "python", "notebooks")
SK_DOC_DIR = os.path.join(DATA_DIR, "upload/docs", "semantic-kernel")

CHROMA_PERSIST_DIR = os.path.join(CUR_DIR, "upload/chroma-persist")
CHROMA_COLLECTION_NAME = "dosu-bot"

from langchain.document_loaders import (
    NotebookLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

LOADER_DICT = {
    "py": TextLoader,
    "md": UnstructuredMarkdownLoader,
    "ipynb": NotebookLoader,
}


def upload_embedding_from_file(file_path):
    loader = LOADER_DICT.get(file_path.split(".")[-1])
    if loader is None:
        raise ValueError("Not supported file type")
    documents = loader(file_path).load()

    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    print(docs, end='\n\n\n')

    Chroma.from_documents(
        docs,
        OpenAIEmbeddings(),
        collection_name=CHROMA_COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
    )
    print('db success')


def upload_embeddings_from_dir(dir_path):
    failed_upload_files = []

    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".py") or file.endswith(".md") or file.endswith(".ipynb"):
                file_path = os.path.join(root, file)

                try:
                    upload_embedding_from_file(file_path)
                    print("SUCCESS: ", file_path)
                except Exception as e:
                    print("FAILED: ", file_path + f"by({e})")
                    failed_upload_files.append(file_path)


upload_embeddings_from_dir(SK_CODE_DIR)
upload_embeddings_from_dir(SK_SAMPLE_DIR)
upload_embeddings_from_dir(SK_DOC_DIR)

from pprint import pprint

db = Chroma(
    persist_directory=CHROMA_PERSIST_DIR,
    embedding_function=OpenAIEmbeddings(),
    collection_name=CHROMA_COLLECTION_NAME,
)

docs = db.similarity_search("i want to know about planner")

pprint(docs)

retriever = db.as_retriever()
retriever.get_relevant_documents("i want to know about planner")
```

endregion

