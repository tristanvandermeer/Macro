from PIL import ImageGrab
import pytesseract
from pytesseract import Output
from pynput.mouse import Button, Controller
import time
import math
import pyautogui  # For screen size

# --------- CONFIGURATION ---------
BOUNDING_BOX = (575, 550, 1150, 950) # one screen bounding
# old BOUNDING_BOX = (900, 550, 1650, 1150)
TARGET_WORD = "malworship"
CLICK_OFFSET_Y = 40
MOVE_DURATION = 1.0
PAUSE_BEFORE_CLICK = 0.5
CHECK_INTERVAL = 15
STOP_MARGIN = 10
# ---------------------------------

mouse = Controller()
SCREEN_W, SCREEN_H = pyautogui.size()
CENTER_X, CENTER_Y = SCREEN_W // 2, SCREEN_H // 2


def mouse_in_corner():
    x, y = mouse.position
    if (
        (x < STOP_MARGIN and y < STOP_MARGIN) or
        (x > SCREEN_W - STOP_MARGIN and y < STOP_MARGIN) or
        (x < STOP_MARGIN and y > SCREEN_H - STOP_MARGIN) or
        (x > SCREEN_W - STOP_MARGIN and y > SCREEN_H - STOP_MARGIN)
    ):
        return True
    return False


def grab_region(bbox):
    return ImageGrab.grab(bbox=bbox)


def read_text_from_image(img):
    return pytesseract.image_to_string(img, lang="eng").strip()


def find_word_bbox(img, word):
    data = pytesseract.image_to_data(img, output_type=Output.DICT, lang="eng")

    for i, txt in enumerate(data["text"]):
        if txt.strip().lower() == word.lower():
            x = data["left"][i]
            y = data["top"][i]
            w = data["width"][i]
            h = data["height"][i]
            return x, y, w, h
    return None


def smooth_move_mouse(x_target, y_target, duration=1.0, steps=120):
    x_start, y_start = mouse.position

    for i in range(steps):
        if mouse_in_corner():
            print("Mouse in corner. Stopping.")
            exit()

        t = (i + 1) / steps
        x = x_start + (x_target - x_start) * t
        y = y_start + (y_target - y_start) * t
        mouse.position = (x, y)
        time.sleep(duration / steps)


def click_with_delay(x, y, pause=0.5):
    print(f"Moving mouse to {x, y}...")
    smooth_move_mouse(x, y, duration=MOVE_DURATION)

    if mouse_in_corner():
        print("Stop detected before click.")
        exit()

    print(f"Pausing for {pause} seconds before clicking...")
    time.sleep(pause)

    if mouse_in_corner():
        print("Stop detected before clicking.")
        exit()

    print("Clicking now.")
    mouse.click(Button.left, 1)


def fallback_center_click():
    # Default to center click to keep game alive
    print("No word detected — clicking center of screen:", (CENTER_X, CENTER_Y))
    click_with_delay(CENTER_X, CENTER_Y, pause=PAUSE_BEFORE_CLICK)


def check_once():
    if mouse_in_corner():
        print("Stop detected before screenshot.")
        exit()

    print("Taking screenshot of:", BOUNDING_BOX)
    img = grab_region(BOUNDING_BOX)

    text = read_text_from_image(img)
    print("OCR detected:")
    print(text)

    bbox = find_word_bbox(img, TARGET_WORD)
    if bbox is None:
        print(f'"{TARGET_WORD}" not found — performing center click.')
        fallback_center_click()
        return

    x_rel, y_rel, w, h = bbox
    print(f"Found '{TARGET_WORD}' at:", bbox)

    left, top, _, _ = BOUNDING_BOX
    click_x = left + x_rel + w // 2
    click_y = top + y_rel + h + CLICK_OFFSET_Y

    print("Final click position:", (click_x, click_y))
    click_with_delay(click_x, click_y, pause=PAUSE_BEFORE_CLICK)


def main():
    print(f"Starting watcher for '{TARGET_WORD}' every {CHECK_INTERVAL} seconds...")
    print("Move your mouse into ANY corner of the screen to stop the script.")

    try:
        while True:
            if mouse_in_corner():
                print("Stop detected! Exiting.")
                break

            print("\n---- New check ----")
            time.sleep(1)
            check_once()

            print(f"Sleeping for {CHECK_INTERVAL} seconds...\n")
            for _ in range(CHECK_INTERVAL * 10):  # check 10× per second
                if mouse_in_corner():
                    print("Stop detected! Exiting.")
                    return
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopped by user.")


if __name__ == "__main__":
    main()
