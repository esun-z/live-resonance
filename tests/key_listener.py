import keyboard

def on_key(e):
    print(f"按键: {e.name}, 类型: {e.event_type}")

keyboard.hook(on_key)
keyboard.wait('esc')  # 按 ESC 退出