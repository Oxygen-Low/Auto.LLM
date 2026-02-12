import argparse
import logging
import sys
import os
from pathlib import Path

# Add the project root to sys.path so we can import Client as a package
sys.path.append(str(Path(__file__).parent.parent))

from Client.config.settings import ConfigLoader
from Client.core.agent import Agent

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
        # For development/testing, we might want to skip strict validation
        # if the user hasn't provided a model yet.
        try:
            config_loader.validate()
        except ValueError as e:
            logging.warning(f"Configuration validation failed: {e}")
            if not args.model and not config_loader.get("model_path"):
                 logging.error("Please provide a model path via config file or --model argument.")
                 # sys.exit(1) # Don't exit yet, let the user see the generated config

        # Initialize and Start Agent
        agent = Agent(config_loader)

        # Check if auto_start intent is set
        if config_loader.get("auto_start"):
            logging.info("Auto-start is enabled in configuration.")

        agent.start()

    except Exception as e:
        logging.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
