# replay_mouse.py
from pynput import mouse
import time
import json

def replay(filename="mouse_recording.json", speed=1.0):
    # speed = 1.0 = real time, 2.0 = twice as fast, 0.5 = half-speed

    with open(filename, "r") as f:
        events = json.load(f)

    # Ensure events are sorted by time
    events.sort(key=lambda e: e["t"])

    m = mouse.Controller()

    if not events:
        print("No events to replay.")
        return

    print(f"Replaying {len(events)} events from {filename} (speed x{speed})")

    start_real = time.perf_counter()
    first_t = events[0]["t"]

    for event in events:
        target_t = (event["t"] - first_t) / speed  # when it *should* happen
        now = time.perf_counter() - start_real

        # Wait until it's time for this event
        delay = target_t - now
        if delay > 0:
            time.sleep(delay)

        etype = event["type"]

        if etype == "move":
            m.position = (event["x"], event["y"])

        elif etype == "click":
            from pynput.mouse import Button
            button_str = event["button"].split(".")[-1].lower()  # 'Button.left' -> 'left'
            button = getattr(Button, button_str, Button.left)

            if event["pressed"]:
                m.press(button)
            else:
                m.release(button)

        elif etype == "scroll":
            m.scroll(event["dx"], event["dy"])

    print("Replay finished.")

if __name__ == "__main__":
    replay()
