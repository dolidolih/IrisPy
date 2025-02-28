# PROJECT_HOME/dataclass/chat_log.py
from dataclasses import dataclass, field
from typing import Optional, Any
from dataclass.v_fields import VFields  # Import VFields
from dataclass.utils import load_json_string

@dataclass
class ChatLog:
    id: str
    _id: str
    deleted_at: str
    referer: int  # Moved up, no default
    type: int
    chat_id: str
    user_id: str
    message: str
    created_at: str
    prev_id: str
    supplement: Optional[Any] = None # Default value
    attachment: Optional[dict] = field(default_factory=lambda: None, metadata={'stringified_json': True}) # attachment as dict, Default value
    v: Optional[VFields] = field(default_factory=lambda: None, metadata={'stringified_json': True}) # v as VFields, Default value

    def __post_init__(self):
        if isinstance(self.attachment, str):
            self.attachment = load_json_string(self.attachment) # Parse attachment to dict
        if isinstance(self.v, str):
            self.v = VFields(**load_json_string(self.v)) if load_json_string(self.v) else None # Parse v to VFields