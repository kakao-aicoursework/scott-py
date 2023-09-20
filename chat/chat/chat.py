"""Welcome to Pynecone! This file outlines the steps to create a basic app."""
import pynecone as pc
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from pynecone.base import Base

from pcconfig import config

docs_url = "https://pynecone.io/docs/getting-started/introduction"
filename = f"{config.app_name}/{config.app_name}.py"

with open("data.txt", "r", encoding="utf-8") as f:
    guide_data = f.read()

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.8)
system_template = f"""\
assistant는 다음 가이드를 참고하여 질문에 답변합니다.

<가이드>
{guide_data}
</가이드>\
"""
human_template = "{question}"


class Message(Base):
    origin_text: str
    output_text: str

    @pc.var
    def origin(self) -> str:
        return "😀 " + self.origin_text

    @pc.var
    def output(self) -> str:
        return "👽 " + self.output_text


def answer_question(question: str) -> Message:
    # chaining prompts
    system_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_prompt = HumanMessagePromptTemplate.from_template(human_template)
    prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

    # get chain object
    chain = LLMChain(llm=llm, prompt=prompt)

    # get answer
    answer = chain.run(
        question=question,
        verbose=True
    )
    return Message(
        origin_text=question,
        output_text=answer
    )


class State(pc.State):
    """The app state."""

    question: str = ""
    messages: list[Message] = []
    is_loading = False

    @pc.var
    def current_question(self) -> str:
        return self.question.strip()

    async def submit(self):
        self.is_loading = True
        yield

        if not self.question.strip():
            return

        msg = answer_question(self.question)
        self.messages.append(msg)
        self.is_loading = False


def header_container():
    return pc.container(
        pc.vstack(
            pc.heading(
                "KAKAO SINC Chatbot",
                margin_top="3rem",
            ),
            pc.text(
                "카카오 싱크에 대해 물어보세요! 😁",
                font_size="14px",
                margin_bottom="2rem",
            ),
        )
    )


def question_container():
    return pc.container(
        pc.hstack(
            pc.input(
                placeholder="",
                on_blur=State.set_question,
            ),
            pc.button(
                "Submit",
                on_click=State.submit,
            ),
            margin_bottom="2rem",
        )
    )


def message_component(msg: Message):
    msg_style = {"border": "solid 1px gray", "border_radius": "5px", "padding": "3px"}
    return pc.container(
        pc.hstack(
            pc.text("😀"),
            pc.box(
                pc.text(msg.origin_text, font_size="12px", color="gray"),
                style=msg_style
            ),
        ),
        pc.hstack(
            pc.box(
                pc.text(msg.output_text, font_size="14px"),
                style=msg_style
            ),
            pc.text("👽", style={"vertial_align": "top"}),
            margin_top="1rem",
        ),
    )


def answer_container():
    return pc.vstack(
        pc.cond(
            State.is_loading,
            pc.spinner(color="black", speed="1s", thickness=5, size="10rem"),
        ),
        pc.foreach(
            State.messages,
            message_component,
        )
    )


def index() -> pc.Component:
    return pc.fragment(
        pc.color_mode_button(pc.color_mode_icon(), float="right"),
        header_container(),
        question_container(),
        answer_container()
    )


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index)
app.compile()
