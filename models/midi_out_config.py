from pydantic import BaseModel

class MidiOutConfig(BaseModel):
    device_name: str = ""
    enabled: bool = False
    merge_channels: bool = False
    target_channel: int = 0