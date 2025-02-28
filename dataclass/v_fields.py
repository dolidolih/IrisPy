from dataclasses import dataclass
from typing import Optional

@dataclass
class VFields:
    notDecoded: Optional[bool] = None
    origin: Optional[str] = None
    c: Optional[str] = None
    modifyRevision: Optional[int] = None
    isSingleDefaultEmoticon: Optional[bool] = None
    defaultEmoticonsCount: Optional[int] = None
    isMine: Optional[bool] = None
    enc: Optional[int] = None