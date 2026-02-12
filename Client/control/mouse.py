import pyautogui
import logging

# Disable PyAutoGUI fail-safe for this application as the LLM needs control
# But we should be careful. Actually, let's keep it enabled but warn.
pyautogui.FAILSAFE = True

def validate_coordinates(x, y):
    screen_width, screen_height = pyautogui.size()
    if not (0 <= x < screen_width and 0 <= y < screen_height):
        raise ValueError(f"Coordinates ({x}, {y}) are out of bounds for screen size {screen_width}x{screen_height}")

def move_to(x, y, duration=0.2):
    try:
        validate_coordinates(x, y)
        pyautogui.moveTo(x, y, duration=duration)
    except Exception as e:
        logging.exception("Error in move_to: %s", e)
        raise

def left_click(x=None, y=None, duration=0.1):
    if (x is None) != (y is None):
        raise ValueError("Both x and y must be provided together or both must be None.")

    try:
        if x is not None and y is not None:
            move_to(x, y, duration=duration)
        pyautogui.click()
    except Exception as e:
        logging.exception("Error in left_click: %s", e)
        raise

def right_click(x=None, y=None, duration=0.1):
    if (x is None) != (y is None):
        raise ValueError("Both x and y must be provided together or both must be None.")

    try:
        if x is not None and y is not None:
            move_to(x, y, duration=duration)
        pyautogui.rightClick()
    except Exception as e:
        logging.exception("Error in right_click: %s", e)
        raise

def drag(start_x, start_y, end_x, end_y, button='left', duration=0.5):
    try:
        validate_coordinates(start_x, start_y)
        validate_coordinates(end_x, end_y)
        pyautogui.moveTo(start_x, start_y)
        pyautogui.dragTo(end_x, end_y, duration=duration, button=button)
    except Exception as e:
        logging.exception("Error in drag: %s", e)
        raise
