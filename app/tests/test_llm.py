import uuid
from pprint import pprint
import pytest
from core.llm import create_answer, generate_answer, clear_history


@pytest.fixture(scope="class")
def conversation_id():
    conversation_id = f"test-{uuid.uuid4()}"
    yield conversation_id
    clear_history(conversation_id)


class TestLLM:
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    test_args = [
        "안녕하세요",
        "너의 이름은 뭐야?",
        "너는 무엇으로 구성되어 있니?",
        "카카오 싱크가 뭐야",
        "그럼 그걸 사용하면 싱크할 수 있어??",
        "카카오 소셜이 뭐야",
        "그게 맞아?",
        "그거 버그 같아",
        "고마워!",
        "카카오 채널에 대해 설명해줘",
    ]

    @pytest.mark.parametrize(
        argnames="user_message",
        argvalues=test_args,
        ids=list(range(len(test_args)))
    )
    def test_create_answer(self, user_message: str, conversation_id: str):
        answer = create_answer(user_message, conversation_id=conversation_id)
        pprint(answer)

    @pytest.mark.parametrize(
        argnames="user_message",
        argvalues=test_args,
        ids=list(range(len(test_args)))
    )
    def test_generate_answer(self, user_message: str, conversation_id: str):
        for res in generate_answer(user_message, conversation_id=conversation_id):
            print(res)
