import os
import sys
import logging
from . import mouse, keyboard, screenshot

class ActionExecutor:
    def __init__(self):
        self.actions = {
            "move_to": mouse.move_to,
            "left_click": mouse.left_click,
            "right_click": mouse.right_click,
            "drag": mouse.drag,
            "type_text": keyboard.type_text,
            "press_key": keyboard.press_key,
            "hotkey": keyboard.hotkey,
            "screenshot": screenshot.capture_screen
        }
        self._check_platform()

    def _check_platform(self):
        if sys.platform.startswith("linux"):
            session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
            if session_type == "wayland":
                logging.warning("Wayland detected. Input injection may fail. X11 is recommended.")

    def execute(self, action_request):
        """
        action_request: dict with "action" and "params"
        Example: {"action": "move_to", "params": {"x": 100, "y": 200}}
        """
        is_valid, error_msg = self.validate_request(action_request)
        if not is_valid:
            return {"status": "error", "message": f"Invalid request: {error_msg}"}

        action_name = action_request.get("action")
        params = action_request.get("params", {})

        if action_name not in self.actions:
            return {"status": "error", "message": f"Unknown action: {action_name}"}

        try:
            func = self.actions[action_name]
            result = func(**params)
            return {"status": "success", "result": result}
        except Exception as e:
            logging.exception("Action execution failed: %s", e)
            return {"status": "error", "message": str(e)}

    def validate_request(self, action_request):
        if not isinstance(action_request, dict):
            return False, "Request must be a JSON object"
        if "action" not in action_request:
            return False, "Missing 'action' field"
        return True, ""
