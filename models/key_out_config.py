from pydantic import BaseModel, Field

class KeyOutConfig(BaseModel):
    enabled: bool = True
    target_process: str = ""
    auto_jump: bool = False
    jump_delay: float = 0.0
    mute_outside_target: bool = True