# record_input.py
from pynput import mouse, keyboard
import time
import json
import threading

events = []
start_time = None
stop_flag = threading.Event()

# Mouse thinning
MOVE_SKIP_EVERY = 2      # record every 2nd movement event
MOVE_MIN_DT = 0.005      # min seconds between recorded moves
_move_count = 0
_last_move_t = 0.0

def ts():
    return time.perf_counter() - start_time

def on_move(x, y):
    global _move_count, _last_move_t
    _move_count += 1

    if _move_count % MOVE_SKIP_EVERY != 0:
        return

    t = ts()
    if t - _last_move_t < MOVE_MIN_DT:
        return
    _last_move_t = t

    events.append({
        "type": "mouse_move",
        "t": t,
        "x": x,
        "y": y,
    })

def on_click(x, y, button, pressed):
    events.append({
        "type": "mouse_click",
        "t": ts(),
        "x": x,
        "y": y,
        "button": str(button),
        "pressed": pressed
    })

def on_scroll(x, y, dx, dy):
    events.append({
        "type": "mouse_scroll",
        "t": ts(),
        "x": x,
        "y": y,
        "dx": dx,
        "dy": dy
    })

def on_key_press(key):
    # Esc to stop recording
    if key == keyboard.Key.esc:
        stop_flag.set()
        return False 

    events.append({
        "type": "key_press",
        "t": ts(),
        "key": str(key)
    })

def on_key_release(key):
    events.append({
        "type": "key_release",
        "t": ts(),
        "key": str(key)
    })

def main():
    global start_time
    start_time = time.perf_counter()

    m_listener = mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll
    )
    k_listener = keyboard.Listener(
        on_press=on_key_press,
        on_release=on_key_release
    )

    m_listener.start()
    k_listener.start()

    print("Recording... press ESC to stop.")
    try:
        while not stop_flag.is_set():
            time.sleep(0.05)
    finally:
        m_listener.stop()
        k_listener.stop()

    events.sort(key=lambda e: e["t"])

    filename = "input_recording.json"
    with open(filename, "w") as f:
        json.dump(events, f, indent=2)

    print(f"Saved {len(events)} events to {filename}")

if __name__ == "__main__":
    main()
