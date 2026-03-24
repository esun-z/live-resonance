from typing import List
from pydantic import BaseModel, Field

# class NoteKeyMap(BaseModel):
#     note: int
#     key: str
#     is_switch: bool = False
#     allow_repeat: bool = False

# class MessageKeyMap(BaseModel):
#     message: bytes
#     key: str

class KeyMapConfig(BaseModel):
    octave_high_offset_switch: str = "left shift"
    octave_low_offset_switch: str = "left ctrl"
    vision_to_low: str = "f1"
    vision_to_mid: str = "f2"
    vision_to_high: str = "f3"
    sustain: str = "space"
    allow_repeat: bool = True
    notes: List[str] = Field(min_length=36, max_length=36, default_factory=lambda: [
        "z", "1", "x", "2", "c", "v", "3", "b", "4", "n", "5", "m",
        "a", "6", "s", "7", "d", "f", "8", "g", "9", "h", "0", "j",
        "q", "i", "w", "o", "e", "r", "p", "t", "[", "y", "]", "u"
    ])
    # notes: Tuple[str, ...] = (
    #     "z",
    #     "1",
    #     "x",
    #     "2",
    #     "c",
    #     "v",
    #     "3",
    #     "b",
    #     "4",
    #     "n",
    #     "5",
    #     "m",
    #     "a",
    #     "6",
    #     "s",
    #     "7",
    #     "d",
    #     "f",
    #     "8",
    #     "g",
    #     "9",
    #     "h",
    #     "0",
    #     "j",
    #     "q",
    #     "i",
    #     "w",
    #     "o",
    #     "e",
    #     "r",
    #     "p",
    #     "t",
    #     "[",
    #     "y",
    #     "]",
    #     "u"
    # )