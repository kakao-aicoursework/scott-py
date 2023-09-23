import os
from enum import Enum
from rxconfig import PROJECT_DIR


# 전처리 후 성공 결과(summary 저장)
SUCCESS_PATH = os.path.join(PROJECT_DIR, "data", "pre", "RESULT.json")


class DataSource(str, Enum):
    """data source"""

    channel = "channel"
    social = "social"
    sync = "sync"

    @property
    def source_path(self) -> str:
        return os.path.join(PROJECT_DIR, "data", f"data_{self}.txt")

    @property
    def dest_path(self) -> str:
        return os.path.join(PROJECT_DIR, "data", "pre", f"{self}.txt")

    def load(self) -> list[str]:
        with open(self.source_path, "r+", encoding="utf-8") as f:
            return f.readlines()

    def dump(self, text: str):
        os.makedirs(os.path.dirname(self.dest_path), exist_ok=True)
        with open(self.dest_path, "w+", encoding="utf-8") as f:
            f.write(text)
