import json
import logging
import time
import traceback
from .context import ContextBuilder
from ..control.actions import ActionExecutor
from ..control.screenshot import image_to_base64
from ..llm.model_loader import ModelLoader
from ..memory.manager import MemoryManager
from ..config.info_loader import load_info

class Agent:
    def __init__(self, config):
        self.config = config
        self.model_loader = ModelLoader(config)
        self.memory_manager = MemoryManager()
        self.action_executor = ActionExecutor()
        self.info_text = load_info()
        self.context_builder = ContextBuilder(self.info_text, self.memory_manager)
        self.running = False

    def start(self):
        logging.info("Starting Agent...")
        self.model_loader.load_models()
        self.running = True
        try:
            self._main_loop()
        except KeyboardInterrupt:
            logging.info("Agent stopped by user.")
        except Exception as e:
            logging.error(f"Agent encountered a fatal error: {e}")
            traceback.print_exc()
        finally:
            self.stop()

    def stop(self):
        logging.info("Stopping Agent...")
        self.running = False
        self.model_loader.unload_models()

    def _main_loop(self):
        while self.running:
            try:
                # 1. Capture State
                screenshot = self.action_executor.execute({"action": "screenshot"})["result"]
                base64_img = image_to_base64(screenshot)

                observation = "New screenshot captured."
                if self.config.get("use_vision_model"):
                    logging.info("Generating screenshot description...")
                    description = self.model_loader.describe_image(base64_img)
                    observation = f"Screenshot description: {description}"
                else:
                    observation = "Screenshot captured (multi-modal support enabled if model supports it)."

                # 2. Build Context
                prompt = self.context_builder.get_full_prompt(observation)

                # 3. Query LLM
                logging.info("Querying LLM...")
                response_text = self.model_loader.generate_completion(prompt)
                logging.info(f"LLM Response: {response_text}")

                # 4. Parse Response
                action_request = self._parse_response(response_text)
                if not action_request:
                    logging.warning("Failed to parse LLM response. Retrying...")
                    time.sleep(1)
                    continue

                # 5. Execute Action
                logging.info(f"Executing action: {action_request}")
                if action_request["action"] == "add_to_high_memory":
                    content = action_request["params"].get("content")
                    if content:
                        try:
                            self.memory_manager.add_to_high_memory(content)
                            result = {"status": "success", "message": "Added to high memory"}
                        except Exception as e:
                            result = {"status": "error", "message": str(e)}
                    else:
                        result = {"status": "error", "message": "Missing content for high memory"}
                else:
                    result = self.action_executor.execute(action_request)

                # 6. Record to Memory
                self.memory_manager.add_event("action", f"Executed {action_request['action']}", {"result": result})
                self.memory_manager.add_event("observation", observation)

                # Small delay between loops
                time.sleep(1)

            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                time.sleep(5)

    def _parse_response(self, text):
        try:
            # Try to find JSON in the response
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = text[start_idx:end_idx+1]
                return json.loads(json_str)
            return None
        except Exception as e:
            logging.error(f"Failed to parse JSON from response: {e}")
            return None
