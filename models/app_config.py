from typing import Optional
from pydantic import BaseModel, Field
from pathlib import Path
import yaml

from .key_map_config import KeyMapConfig
from .midi_in_config import MidiInConfig
from .midi_out_config import MidiOutConfig
from .key_out_config import KeyOutConfig
from .player_config import PlayerConfig

class AppConfig(BaseModel):
    key_map: KeyMapConfig = Field(default_factory=KeyMapConfig)
    midi_in: MidiInConfig = Field(default_factory=MidiInConfig)
    midi_out: MidiOutConfig = Field(default_factory=MidiOutConfig)
    key_out: KeyOutConfig = Field(default_factory=KeyOutConfig)
    player: PlayerConfig = Field(default_factory=PlayerConfig)

    def save_to_yaml(self, path: str) -> bool:
        path: Path = Path(path)
        data_dict = self.model_dump(mode="json")
        try:
            with path.open("w", encoding="utf-8") as file:
                yaml.dump(data_dict, file, allow_unicode=True, default_flow_style=False)
                return True

        except:
            return False

    @classmethod
    def load_from_yaml(cls, path: str) -> Optional["AppConfig"]:
        path = Path(path)
        if not path.is_file():
            return None

        try:
            with path.open("r", encoding="utf-8") as file:
                data_dict = yaml.safe_load(file)
                return AppConfig.model_validate(data_dict)
        except:
            return None

