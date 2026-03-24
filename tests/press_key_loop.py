import keyboard
import time

def press_and_release(key_name: str, duration: float = 0.1):
    # pydirectinput.keyDown(key_name)
    # time.sleep(duration)
    # pydirectinput.keyUp(key_name)
    keyboard.press_and_release(key_name)
    # keyboard.press(key_name)
    # time.sleep(duration)
    # keyboard.release(key_name)

if __name__ == "__main__":
    for i in range(5):
        print(f"Starting in {5 - i} seconds...")
        time.sleep(1)

    try:
        while True:
            # ok: octave switch
            # for i in range(3):
            # # press_and_release('left shift', duration=0.05)
            #     keyboard.press('left shift')
            #     if i == 0:
            #         press_and_release('f1')
            #     elif i == 1:
            #         press_and_release('f2')
            #     else:
            #         press_and_release('f3')
            #     print(f"Pressed and released f{i + 1}")
            #     time.sleep(0.05)
            #     keyboard.release('left shift')
            #     print("Pressed and released left shift")
            #     time.sleep(2)

            for i in range(2):
                
                if i == 0:
                    keyboard.press('left shift')
                    press_and_release('f1')
                    time.sleep(0.05)
                    press_and_release('a')
                    keyboard.release('left shift')
                    
                else:
                    press_and_release('left ctrl')
                    press_and_release('f2')
                    time.sleep(0.05)
                    press_and_release('a')
                
                time.sleep(2)
    except KeyboardInterrupt:
        print("Exiting...")