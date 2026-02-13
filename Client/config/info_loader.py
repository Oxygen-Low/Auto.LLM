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
            # Add placeholder to the generated file but not to the base template variable
            content_with_placeholder = INFO_TEMPLATE + "\nMachine Password: [INSERT_PASSWORD_HERE]\n"
            with open(path, "w") as f:
                f.write(content_with_placeholder)
            content = content_with_placeholder
        except Exception:
            logger.exception("Error creating info.txt template")
            return ""
    else:
        try:
            with open(path, "r") as f:
                content = f.read()
        except Exception:
            logger.exception("Error reading info.txt")
            return ""

    # Inject secrets from environment variables
    # We replace any existing Machine Password line
    # Note: We redact the actual password when returning info to be safe
    password_line = "Machine Password: [REDACTED]"

    if re.search(r"^Machine Password:.*", content, re.MULTILINE):
        content = re.sub(r"^Machine Password:.*", password_line, content, flags=re.MULTILINE)

    return content
