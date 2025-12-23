from pynput import mouse, keyboard
import time
import json

SAFE_CORNER_THRESHOLD = 5  # pixels from (0,0)

def parse_key(key_str):
    """
    Convert the recorded string back to something keyboard.Controller can use.
    key_str looks like:
      - "'a'" for normal chars
      - "Key.space", "Key.enter", ...
    """
    # Special keys
    if key_str.startswith("Key."):
        name = key_str.split(".", 1)[1]
        return getattr(keyboard.Key, name, None)

    # For "'a'" style reprs, strip quotes
    if key_str.startswith("'") and key_str.endswith("'") and len(key_str) == 3:
        return key_str[1]

    # Fallback: just return the raw string (won't always work, but okay as backup)
    return key_str

def parse_button(button_str):
    # button_str like 'Button.left'
    from pynput.mouse import Button
    if button_str.startswith("Button."):
        name = button_str.split(".", 1)[1]
        return getattr(Button, name, Button.left)
    return Button.left

def replay(filename="input_recording.json", speed=1.0):
    with open(filename, "r") as f:
        events = json.load(f)

    if not events:
        print("No events to replay.")
        return

    # Ensure sorted
    events.sort(key=lambda e: e["t"])

    m = mouse.Controller()
    k = keyboard.Controller()

    print(f"Replaying {len(events)} events from {filename} at speed x{speed}")
    print("Safety: move mouse to top-left corner to stop.")

    start_real = time.perf_counter()
    first_t = events[0]["t"]

    for event in events:
        # Safety breakout: check mouse pos every event
        x, y = m.position
        if x <= SAFE_CORNER_THRESHOLD and y <= SAFE_CORNER_THRESHOLD:
            print("Safety corner reached, stopping replay.")
            break

        target_t = (event["t"] - first_t) / speed
        now = time.perf_counter() - start_real
        delay = target_t - now
        if delay > 0:
            time.sleep(delay)

        etype = event["type"]

        if etype == "mouse_move":
            m.position = (event["x"], event["y"])

        elif etype == "mouse_click":
            button = parse_button(event["button"])
            if event["pressed"]:
                m.press(button)
            else:
                m.release(button)

        elif etype == "mouse_scroll":
            m.scroll(event["dx"], event["dy"])

        elif etype == "key_press":
            key_obj = parse_key(event["key"])
            if key_obj is not None:
                k.press(key_obj)

        elif etype == "key_release":
            key_obj = parse_key(event["key"])
            if key_obj is not None:
                k.release(key_obj)

    print("Replay finished.")

if __name__ == "__main__":
    replay()
