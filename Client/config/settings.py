import json
import os
import sys
import shlex
import logging
from pathlib import Path

DEFAULT_CONFIG = {
    "model_path": "",
    "model_directory": "models",
    "auto_start": False,
    "use_vision_model": False,
    "vision_model_path": "",
    "clip_model_path": "",
    "context_size": 2048,
    "n_gpu_layers": 0,
    "typing_interval": 0.05,
    "action_duration": 0.2
}

logger = logging.getLogger(__name__)

class ConfigLoader:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).resolve().parent / "client_config.json"
        self.config_path = Path(config_path)
        self.settings = DEFAULT_CONFIG.copy()
        self._load_config()

    def _load_config(self):
        if not self.config_path.exists():
            self._save_config()
        else:
            try:
                with open(self.config_path, "r") as f:
                    user_settings = json.load(f)
                    for key, value in user_settings.items():
                        if key in self.settings:
                            self.settings[key] = value
                        else:
                            logger.warning(f"Unknown configuration key ignored: {key}")
            except Exception as e:
                logger.error(f"Error loading config: {e}. Using defaults.")

    def _save_config(self):
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            logger.exception("Error saving config: %s", e)

    def handle_autostart(self):
        """Public method to trigger autostart configuration based on current settings."""
        if sys.platform.startswith("linux"):
            self._setup_linux_autostart()
        elif sys.platform == "win32":
            # TODO: Implement Windows auto-start
            pass

    def _setup_linux_autostart(self):
        autostart_dir = Path.home() / ".config" / "autostart"
        desktop_file = autostart_dir / "auto_llm_client.desktop"

        if self.settings.get("auto_start"):
            try:
                autostart_dir.mkdir(parents=True, exist_ok=True)
                # We assume main.py is in the parent of the config directory
                # But since we're in Client/config, it's in Client/
                script_path = Path(__file__).parent.parent / "main.py"
                exec_command = f"{shlex.quote(sys.executable)} {shlex.quote(str(script_path.absolute()))}"
                content = f"""[Desktop Entry]
Type=Application
Exec={exec_command}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Auto.LLM Client
Comment=LLM Computer Control Client
"""
                with open(desktop_file, "w") as f:
                    f.write(content)
            except Exception as e:
                logger.exception("Failed to set up Linux autostart: %s", e)
        else:
            if desktop_file.exists():
                try:
                    desktop_file.unlink()
                except Exception as e:
                    logger.exception("Failed to remove Linux autostart: %s", e)

    def _resolve_model_path(self, path_str, field_name):
        if not path_str:
            raise ValueError(f"Configuration Error: '{field_name}' is required.")

        path = Path(path_str)
        if not path.is_absolute():
            model_dir = Path(self.settings.get("model_directory", "models"))
            if not model_dir.is_absolute():
                model_dir = Path(__file__).resolve().parent.parent.parent / model_dir

            alt_path = model_dir / path
            if alt_path.exists():
                return str(alt_path.absolute())
            elif path.exists():
                return str(path.absolute())
            else:
                raise ValueError(f"Configuration Error: {field_name} '{path}' does not exist.")
        elif not path.exists():
            raise ValueError(f"Configuration Error: {field_name} '{path}' does not exist.")

        return str(path.absolute())

    def validate(self):
        self.settings["model_path"] = self._resolve_model_path(
            self.settings.get("model_path"), "model_path"
        )

        # Validate vision settings if enabled
        if self.settings.get("use_vision_model"):
            for field in ["vision_model_path", "clip_model_path"]:
                self.settings[field] = self._resolve_model_path(
                    self.settings.get(field), field
                )

    def get(self, key, default=None):
        return self.settings.get(key, default)
