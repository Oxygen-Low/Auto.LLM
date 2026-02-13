import argparse
import logging
import sys

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
    parser.add_argument("--config", type=str, default=None, help="Path to config file")
    parser.add_argument("--model", type=str, help="Override model path")
    parser.add_argument("--run", action="store_true", help="Force start the agent regardless of auto_start setting")
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
            logging.error("Configuration validation failed: %s", e)
            sys.exit(1)

        # Handle OS-level auto-start registration
        config_loader.handle_autostart()

        should_run = args.run or config_loader.get("auto_start")

        if should_run:
            if args.run:
                logging.info("Starting Agent via CLI flag.")
            else:
                logging.info("Auto-start is enabled. Starting Agent.")

            # Initialize and Start Agent
            agent = Agent(config_loader)
            agent.start()
        else:
            logging.info("Neither --run flag nor auto_start are enabled. Skipping Agent startup.")

    except Exception:
        logging.exception("Failed to start application")
        sys.exit(1)

if __name__ == "__main__":
    main()
