import argparse
import logging
import sys
import os
from pathlib import Path

# Package is expected to be run as 'python -m Client.main'
# No sys.path manipulation needed if run correctly.

from .config.settings import ConfigLoader
from .core.agent import Agent

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="Auto.LLM Client - LLM Computer Control")
    parser.add_argument("--config", type=str, default="Client/config/client_config.json", help="Path to config file")
    parser.add_argument("--model", type=str, help="Override model path")
    args = parser.parse_args()

    try:
        # Load Configuration
        config_loader = ConfigLoader(args.config)

        # Override model path if provided via CLI
        if args.model:
            config_loader.settings["model_path"] = args.model

        # Validate configuration
        try:
            config_loader.validate()
        except ValueError as e:
            logging.error(f"Configuration validation failed: {e}")
            sys.exit(1)

        # Handle OS-level auto-start registration
        config_loader.handle_autostart()
        if config_loader.get("auto_start"):
            logging.info("Auto-start registration updated in system.")

        # Initialize and Start Agent
        agent = Agent(config_loader)
        agent.start()

    except Exception as e:
        logging.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
