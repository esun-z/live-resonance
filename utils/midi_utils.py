import mido
from typing import List, Optional

note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def decode_midi_text(text: str, charset: Optional[str] = None) -> tuple[str, str]:
    if charset is not None:
        try:
            return (text.encode('latin1').decode(charset), charset)
        except Exception:
            pass
    encodings = ['utf-8', 'gbk', 'gb18030', 'big5', 'utf-16', 'latin1']
    for encoding in encodings:
        try:
            return (text.encode('latin1').decode(encoding), encoding)
        except Exception:
            pass

    return (text, 'latin1')

def is_note_message(msg: mido.Message) -> bool:
    return msg.type in ['note_on', 'note_off']

def is_note_on(msg: mido.Message) -> bool:
    return msg.type == 'note_on' and msg.velocity > 0

def is_note_off(msg: mido.Message) -> bool:
    return (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0)

def is_padel_message(msg: mido.Message) -> bool:
    return msg.type == 'control_change' and msg.control == 64

def is_padel_on(msg: mido.Message) -> bool:
    return is_padel_message(msg) and msg.value >= 64

def is_padel_off(msg: mido.Message) -> bool:
    return is_padel_message(msg) and msg.value < 64

def is_message_in_channels(msg: mido.Message, enabled_channels: List[bool], no_channel_msg_result: bool = True) -> bool:
    if hasattr(msg, 'channel'):
        return enabled_channels[msg.channel]
    return no_channel_msg_result

def get_note_octave(note: int) -> int: # using MIDI octave instead of musical octave
    return note // 12

def set_message_channel(msg: mido.Message, target_channel: int) -> mido.Message:
    # deep copy
    message = msg.copy()
    if hasattr(message, 'channel'):
        message.channel = target_channel
    return message

def get_note_name(note: int, is_musical: bool = False) -> str:
    octave = get_note_octave(note) - (1 if is_musical else 0)
    name = note_names[note % 12]
    return f"{name}{octave}"