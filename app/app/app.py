"""Welcome to Pynecone! This file outlines the steps to create a basic app."""
import asyncio
from typing import Literal

import reflex as rx

from core import generate_answer
from rxconfig import config

docs_url = "https://pynecone.io/docs/getting-started/introduction"
filename = f"{config.app_name}/{config.app_name}.py"


class State(rx.State):
    """The app state."""

    question: str = ""
    chat_history: list[tuple[Literal["user", "bot"], str]]
    is_loading = False

    async def submit(self):
        if self.is_loading:
            return

        if not self.question.strip():
            return

        # add chat history
        self.chat_history.append(("user", self.question.strip()))
        self.is_loading = True
        yield

        # send question -> get answer
        self.chat_history.append(("bot", ""))
        for res in generate_answer(self.question):
            self.is_loading = False
            self.chat_history[-1] = ("bot", self.chat_history[-1][1] + res)
            yield
            await asyncio.sleep(0.05)


def header_container():
    return rx.container(
        rx.vstack(
            rx.heading(
                "KAKAO Chatbot",
                margin_top="3rem",
            ),
            rx.text(
                "모든지 물어보세요! 😁",
                font_size="14px",
                margin_bottom="2rem",
            ),
        )
    )


def question_container():
    return rx.container(
        rx.hstack(
            rx.input(
                placeholder="",
                on_blur=State.set_question,
            ),
            rx.button(
                "Submit",
                on_click=State.submit,
                is_disabled=State.is_loading,
            ),
            margin_bottom="2rem",
        )
    )


def user_msg_component(msg: str):
    return rx.container(
        rx.flex(
            rx.box(
                rx.text(msg, font_size="14px", color="gray"),
                style={
                    "color": "black",
                    "border": "solid 1px gray",
                    "border_radius": "5px",
                    "padding": "3px",
                    "background_color": "#f1f2f5",
                    "max_width": "70%"
                }
            ),
            rx.box(rx.text(" 😀"), margin_left="1rem"),
            justify="flex-end",
            margin_top="1rem",
            style={"width": "100%"}
        ),
    )


def bot_msg_component(msg: str):
    return rx.container(
        rx.flex(
            rx.box(
                rx.text("👽 "),
                margin_right="1rem"
            ),
            rx.box(
                rx.text(msg, font_size="14px"),
                style={
                    "color": "white",
                    "border": "solid 1px gray",
                    "border_radius": "5px",
                    "padding": "3px",
                    "background_color": "#3b81f5",
                    "max_width": "70%"
                }
            ),
            justify="flex-start",
            margin_top="1rem",
            style={"width": "100%"}
        ),
    )


def message_component(msg_type: Literal["bot", "user"], msg: str):
    return rx.container(
        rx.cond(
            msg_type == "user",
            user_msg_component(msg),
            bot_msg_component(msg)
        )
    )


def answer_container():
    return rx.vstack(
        rx.container(
            bot_msg_component("안녕하세요. 챗봇 서비스를 시작합니다. 궁금하신 내용을 물어보세요!")
        ),
        rx.foreach(
            State.chat_history,
            lambda message: message_component(message[0], message[1]),
        ),
        rx.cond(
            State.is_loading,
            rx.spinner(color="lightgreen", speed="1s", thickness=5, size="xl"),
        ),
    )


def index() -> rx.Component:
    return rx.fragment(
        rx.color_mode_button(rx.color_mode_icon(), float="right"),
        header_container(),
        question_container(),
        answer_container()
    )


# Add state and page to the app.
app = rx.App(state=State)
app.add_page(index)
app.compile()
