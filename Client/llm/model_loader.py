import logging
from llama_cpp import Llama
try:
    from llama_cpp.llava import LlavaChatHandler
except ImportError:
    LlavaChatHandler = None

class ModelLoader:
    def __init__(self, config):
        self.config = config
        self.text_model = None
        self.vision_model = None
        self.vision_model_failed = False
        self.vision_model_error = None

    def load_models(self):
        model_path = self.config.get("model_path")
        if not model_path:
            raise ValueError("model_path not specified in config")

        try:
            logging.info("Loading text model from %s...", model_path)
            self.text_model = Llama(
                model_path=model_path,
                n_ctx=self.config.get("context_size", 2048),
                n_gpu_layers=self.config.get("n_gpu_layers", 0),
                verbose=False
            )
            logging.info("Text model loaded successfully.")
        except Exception:
            logging.exception("Failed to load text model")
            raise

        if self.config.get("use_vision_model"):
            vision_model_path = self.config.get("vision_model_path")
            clip_model_path = self.config.get("clip_model_path")

            if not vision_model_path:
                logging.warning("use_vision_model is True but vision_model_path is not specified.")
            else:
                try:
                    chat_handler = None
                    if clip_model_path and LlavaChatHandler:
                        logging.info("Initializing vision chat handler with %s...", clip_model_path)
                        chat_handler = LlavaChatHandler(clip_model_path=clip_model_path)

                    logging.info("Loading vision model from %s...", vision_model_path)
                    self.vision_model = Llama(
                        model_path=vision_model_path,
                        chat_handler=chat_handler,
                        n_ctx=self.config.get("context_size", 2048),
                        n_gpu_layers=self.config.get("n_gpu_layers", 0),
                        verbose=False
                    )
                    logging.info("Vision model loaded successfully.")
                except Exception as e:
                    self.vision_model_failed = True
                    self.vision_model_error = e
                    logging.exception("Failed to load vision model")

    def generate_completion(self, prompt, max_tokens=512, stop=None):
        if not self.text_model:
            raise RuntimeError("Text model not loaded")

        response = self.text_model(
            prompt,
            max_tokens=max_tokens,
            stop=stop,
            echo=False
        )
        return response['choices'][0]['text']

    def describe_image(self, base64_image):
        """
        Generates a description of the provided base64 image using the vision model.
        """
        if self.vision_model_failed:
            return f"Vision model failed to load: {self.vision_model_error}"
        if not self.vision_model:
            return "Vision model not configured."

        # Note: For multi-modal GGUF (like LLaVA), llama-cpp-python typically needs
        # a CLIP adapter. This implementation assumes the vision_model is either
        # a multi-modal model or handles image input via a chat-like interface.

        try:
            # If the model is a Chat completion compatible model, we use chat format
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this computer screen for a text-based AI assistant. What do you see? What windows are open? What are the coordinates of important elements?"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                    ]
                }
            ]

            # This requires the vision_model to have a chat_handler set up during initialization.
            response = self.vision_model.create_chat_completion(
                messages=messages,
                max_tokens=512
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            logging.exception("Vision description failed")
            return f"Error describing image: {e}"

    def unload_models(self):
        if self.text_model:
            del self.text_model
            self.text_model = None
        if self.vision_model:
            del self.vision_model
            self.vision_model = None

        # Reset failure states
        self.vision_model_failed = False
        self.vision_model_error = None
