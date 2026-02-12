import pyautogui
import logging

def type_text(text, interval=0.05):
    try:
        pyautogui.write(text, interval=interval)
    except Exception as e:
        logging.error(f"Error in type_text: {e}")
        raise

def press_key(key):
    try:
        # PyAutoGUI handles special keys if they are in its KEYBOARD_KEYS list
        pyautogui.press(key)
    except Exception as e:
        logging.error(f"Error in press_key: {e}")
        raise

def hotkey(*keys):
    try:
        pyautogui.hotkey(*keys)
    except Exception as e:
        logging.error(f"Error in hotkey: {e}")
        raise
