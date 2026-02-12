import pyautogui
import logging
import sys
try:
    import pyperclip
except ImportError:
    pyperclip = None

def type_text(text, interval=0.05):
    # Check if text is ASCII
    is_ascii = all(ord(c) < 128 for c in text)

    if is_ascii:
        try:
            logging.info("Typing text via pyautogui.write")
            pyautogui.write(text, interval=interval)
            return
        except Exception as e:
            logging.exception("Error in pyautogui.write: %s. Attempting fallback.", e)

    # Non-ASCII or failed ASCII write
    try:
        _type_text_fallback(text)
    except Exception as fallback_e:
        logging.exception("Fallback type_text failed: %s", fallback_e)
        raise

def _type_text_fallback(text):
    if pyperclip is None:
        raise ImportError("pyperclip is required for non-ASCII text fallback")

    logging.info("Typing text via pyperclip fallback")
    pyperclip.copy(text)
    if sys.platform == "darwin":
        pyautogui.hotkey("command", "v")
    else:
        pyautogui.hotkey("ctrl", "v")

def press_key(key):
    try:
        # PyAutoGUI handles special keys if they are in its KEYBOARD_KEYS list
        pyautogui.press(key)
    except Exception as e:
        logging.exception("Error in press_key: %s", e)
        raise

def hotkey(*keys):
    try:
        pyautogui.hotkey(*keys)
    except Exception as e:
        logging.exception("Error in hotkey: %s", e)
        raise
