import mss
import mss.tools
from PIL import Image
import io
import base64
import logging

def capture_screen(region=None):
    """
    Captures the screen.
    region: tuple of (left, top, width, height)
    Returns a PIL Image object.
    """
    try:
        with mss.mss() as sct:
            if region:
                left, top, width, height = region
                monitor = {"top": top, "left": left, "width": width, "height": height}
            else:
                monitor = sct.monitors[1] # Primary monitor

            sct_img = sct.grab(monitor)
            return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    except Exception as e:
        logging.error(f"Error in capture_screen: {e}")
        # Fallback to PyAutoGUI
        import pyautogui
        return pyautogui.screenshot(region=region)

def image_to_base64(image):
    try:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        logging.error(f"Error in image_to_base64: {e}")
        return ""

def save_image(image, filepath):
    try:
        image.save(filepath)
    except Exception as e:
        logging.error(f"Error saving image: {e}")
