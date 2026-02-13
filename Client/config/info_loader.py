import os
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

INFO_TEMPLATE = """# Auto.LLM User Context Information
# Use this file to provide specific information about the machine to the LLM.
#
# WARNING: DO NOT STORE SENSITIVE DATA (like passwords) IN THIS FILE.
# Sensitive information should be provided via environment variables
# or a secure secrets manager.
#
# Format: Key: Value (or just plain text)
# Lines starting with # are comments.

Server IP: 127.0.0.1
Accessible Ports: 80, 443, 8000, 8080
"""

def load_info(info_path=None):
    if info_path is None:
        info_path = Path(__file__).resolve().parent / "info.txt"

    path = Path(info_path)
    if not path.exists():
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                f.write(INFO_TEMPLATE)
            content = INFO_TEMPLATE
        except Exception as e:
            logger.exception("Error creating info.txt template: %s", e)
            return ""
    else:
        try:
            with open(path, "r") as f:
                content = f.read()
        except Exception as e:
            logger.exception("Error reading info.txt: %s", e)
            return ""

    # Inject secrets from environment variables
    # We replace any existing Machine Password line or append if not present
    # Note: We redact the actual password when returning info to be safe
    password_line = "Machine Password: [REDACTED]"

    if re.search(r"^Machine Password:.*", content, re.MULTILINE):
        content = re.sub(r"^Machine Password:.*", password_line, content, flags=re.MULTILINE)
    else:
        content += f"\n{password_line}\n"

    return content
