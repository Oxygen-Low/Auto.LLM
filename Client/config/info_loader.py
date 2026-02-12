import os
from pathlib import Path

INFO_TEMPLATE = """# Auto.LLM User Context Information
# Use this file to provide specific information about the machine to the LLM.
# Format: Key: Value (or just plain text)
# Lines starting with # are comments.

Machine Password: [INSERT_PASSWORD_HERE]
Server IP: 127.0.0.1
Accessible Ports: 80, 443, 8000, 8080
"""

def load_info(info_path="Client/config/info.txt"):
    path = Path(info_path)
    if not path.exists():
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                f.write(INFO_TEMPLATE)
            return INFO_TEMPLATE
        except Exception as e:
            print(f"Error creating info.txt template: {e}")
            return ""

    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading info.txt: {e}")
        return ""
