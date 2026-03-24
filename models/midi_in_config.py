from pydantic import BaseModel, Field
from typing import List

class MidiInConfig(BaseModel):
    device_name: str = ""
    enabled: bool = False
    enabled_channels: List[bool] = Field(min_length=16, max_length=16, default_factory=lambda: [True]*16)