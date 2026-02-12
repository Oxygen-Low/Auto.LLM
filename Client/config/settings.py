import json
import os
import sys
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

class ConfigLoader:
    def __init__(self, config_path="Client/config/client_config.json"):
        self.config_path = Path(config_path)
        self.settings = DEFAULT_CONFIG.copy()
        self._load_config()
        self._handle_autostart()

    def _load_config(self):
        if not self.config_path.exists():
            self._save_config()
        else:
            try:
                with open(self.config_path, "r") as f:
                    user_settings = json.load(f)
                    self.settings.update(user_settings)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")

    def _save_config(self):
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def _handle_autostart(self):
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
                content = f"""[Desktop Entry]
Type=Application
Exec={sys.executable} {script_path.absolute()}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Auto.LLM Client
Comment=LLM Computer Control Client
"""
                with open(desktop_file, "w") as f:
                    f.write(content)
            except Exception as e:
                print(f"Failed to set up Linux autostart: {e}")
        else:
            if desktop_file.exists():
                try:
                    desktop_file.unlink()
                except Exception as e:
                    print(f"Failed to remove Linux autostart: {e}")

    def validate(self):
        if not self.settings.get("model_path"):
            raise ValueError("Configuration Error: 'model_path' is required.")

        model_path = Path(self.settings["model_path"])
        if not model_path.is_absolute():
            # Try relative to model_directory if it's set
            model_dir = Path(self.settings.get("model_directory", "models"))
            if not model_dir.is_absolute():
                # Assuming model_dir is relative to project root (parent of Client/)
                model_dir = Path(__file__).parent.parent.parent / model_dir

            alt_path = model_dir / model_path
            if alt_path.exists():
                self.settings["model_path"] = str(alt_path.absolute())
            else:
                # Still check if it exists as relative to current working dir
                if not model_path.exists():
                     raise ValueError(f"Configuration Error: model_path '{model_path}' does not exist.")
        elif not model_path.exists():
             raise ValueError(f"Configuration Error: model_path '{model_path}' does not exist.")

    def get(self, key):
        return self.settings.get(key)
