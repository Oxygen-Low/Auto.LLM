import json
import logging
import time
import re
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
        self._stopped = False
        self.consecutive_errors = 0
        self.max_consecutive_errors = config.get("max_consecutive_errors", 5)
        self.base_backoff = config.get("base_backoff", 1.0)

    def start(self):
        logging.info("Starting Agent...")
        try:
            self.model_loader.load_models()
            self.running = True
            self._stopped = False
            self._main_loop()
        except KeyboardInterrupt:
            logging.info("Agent stopped by user.")
        except Exception as e:
            logging.exception("Agent encountered a fatal error: %s", e)
        finally:
            self.stop()

    def stop(self):
        if self._stopped:
            return
        logging.info("Stopping Agent...")
        self.running = False
        if self.model_loader:
            try:
                self.model_loader.unload_models()
            except Exception as e:
                logging.exception("Error unloading models: %s", e)
        self._stopped = True

    def _main_loop(self):
        while self.running:
            try:
                # 1. Capture State
                response = self.action_executor.execute({"action": "screenshot"})
                if response.get("status") == "error":
                    raise RuntimeError(f"Failed to capture screenshot: {response.get('message')}")

                screenshot = response.get("result")
                if screenshot is None:
                    raise RuntimeError("Screenshot action returned success but no result.")

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
                logging.debug("LLM Response (full): %s", response_text)
                logging.info("LLM Response (truncated): %s", response_text[:100] + ("..." if len(response_text) > 100 else ""))

                # 4. Parse Response
                action_request = self._parse_response(response_text)
                if not action_request:
                    logging.warning("Failed to parse LLM response. Retrying...")
                    time.sleep(1)
                    continue

                # 5. Execute Action
                if not isinstance(action_request, dict) or "action" not in action_request:
                    result = {"status": "error", "message": "Malformed action_request: missing 'action'"}
                else:
                    logging.info(f"Executing action: {action_request.get('action')}")
                    action_name = action_request["action"]
                    params = action_request.get("params", {})

                    if action_name == "add_to_high_memory":
                        if isinstance(params, dict) and "content" in params:
                            content = params["content"]
                            try:
                                self.memory_manager.add_to_high_memory(content)
                                result = {"status": "success", "message": "Added to high memory"}
                            except Exception as e:
                                result = {"status": "error", "message": str(e)}
                        else:
                            result = {"status": "error", "message": "Malformed action_request: missing 'params/content'"}
                    else:
                        result = self.action_executor.execute(action_request)

                # 6. Record to Memory
                if isinstance(action_request, dict) and "action" in action_request:
                    self.memory_manager.add_event("action", f"Executed {action_request['action']}", {"result": result})
                self.memory_manager.add_event("observation", observation)

                self.consecutive_errors = 0
                # Small delay between loops
                time.sleep(1)

            except Exception as e:
                self.consecutive_errors += 1
                logging.exception("Error in main loop (error %d/%d): %s",
                                  self.consecutive_errors, self.max_consecutive_errors, e)

                if self.consecutive_errors >= self.max_consecutive_errors:
                    logging.error("Max consecutive errors reached. Triggering shutdown.")
                    self.stop()
                    break

                backoff_delay = self.base_backoff * (2 ** min(self.consecutive_errors, 6))
                logging.info("Waiting %.2f seconds before retry...", backoff_delay)
                time.sleep(backoff_delay)

    def _parse_response(self, text):
        # 1. Look for fenced JSON blocks
        fenced_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if fenced_match:
            try:
                return json.loads(fenced_match.group(1))
            except json.JSONDecodeError:
                pass

        # 2. Robust balanced brace extraction
        candidates = []
        stack = 0
        start = -1
        for i, char in enumerate(text):
            if char == '{':
                if stack == 0:
                    start = i
                stack += 1
            elif char == '}':
                if stack > 0:
                    stack -= 1
                    if stack == 0:
                        candidates.append(text[start:i+1])

        for cand in candidates:
            try:
                return json.loads(cand)
            except json.JSONDecodeError:
                continue

        return None
