import os

os.environ["VERBOSE"] = "true"

from core import init


def pytest_sessionstart():
    init()
