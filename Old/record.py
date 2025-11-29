import pynput, time

# record_mouse.py
from pynput import mouse
import time
import json

events = []
start_time = None

def now():
    return time.perf_counter() - start_time

def on_move(x, y):
    events.append({
        "type": "move",
        "t": now(),
        "x": x,
        "y": y,
    })

def on_click(x, y, button, pressed):
    events.append({
        "type": "click",
        "t": now(),
        "x": x,
        "y": y,
        "button": str(button),   # e.g. 'Button.left'
        "pressed": pressed,      # True on press, False on release
    })

def on_scroll(x, y, dx, dy):
    events.append({
        "type": "scroll",
        "t": now(),
        "x": x,
        "y": y,
        "dx": dx,
        "dy": dy,
    })

def main():
    global start_time
    start_time = time.perf_counter()

    listener = mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll
    )

    print("Recording... press Ctrl+C to stop.")
    listener.start()
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping...")
        listener.stop()

    # Save to file
    filename = "mouse_recording.json"
    with open(filename, "w") as f:
        json.dump(events, f, indent=2)

    print(f"Saved {len(events)} events to {filename}")

if __name__ == "__main__":
    main()