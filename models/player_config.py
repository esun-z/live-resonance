from pydantic import BaseModel
from enum import Enum

class OutOfRangeStrategy(str, Enum):
    IGNORE = "ignore"
    TO_NEAREST = "to nearest octave"

class OctaveStrategy(str, Enum):
    DEFAULT_ONLY = "default only"
    AUTO_LATCH = "auto latch"
    LATCH_HIGH = "auto latch and protect higher octaves"
    LATCH_LOW = "auto latch and protect lower octaves"
    MANUAL = "manual"

class PlayerConfig(BaseModel):
    min_note: int = 21 # 48 # 21 (A1 MIDI, A0 Musical) for 88 keys piano
    max_note: int = 95 # 108 for 88 keys piano
    vision_base_octave: int = 4
    high_out_of_range_strategy: OutOfRangeStrategy = OutOfRangeStrategy.TO_NEAREST
    low_out_of_range_strategy: OutOfRangeStrategy = OutOfRangeStrategy.TO_NEAREST
    octave_strategy: OctaveStrategy = OctaveStrategy.LATCH_HIGH
    note_after_octave_switch_ms: int = 60
    min_padel_interval_ms: int = 100
    octave_switch_cooldown_ms: int = 200
    clean_switch: bool = False
    ignore_note_softer_than: int = 10