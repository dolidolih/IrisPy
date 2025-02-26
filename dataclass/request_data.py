from dataclasses import dataclass, field
from typing import Optional
from dataclass.chat_log import ChatLog  # Assuming chat_log.py is in the same directory
from dataclass.utils import load_json_string

@dataclass
class RequestData:
    room: str
    msg: str
    sender: str
    json: Optional[ChatLog] = field(default_factory=lambda: None, metadata={'stringified_json': True})

    def __post_init__(self):
        if isinstance(self.json, str):
            self.json = ChatLog(**load_json_string(self.json)) if load_json_string(self.json) else None