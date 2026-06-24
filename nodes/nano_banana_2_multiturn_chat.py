import io, torch, numpy as np
from PIL import Image

from google import genai
from google.genai import types

from ..core.auth import detect_approach, PROJECT_ID, LOCATION, GOOGLE_API_KEY
from ..utils.image_utils import tensor_to_pil

class NanoBanana2MultiTurnChat:
    """
    Nano Banana 2 Multi-Turn Chat node using gemini-3.1-flash-image model.
    Supports conversational image generation and editing with preserved context.
    Features:
    - Up to 14 reference images (10 objects + 4 characters)
    - New aspect ratios: 1:4, 4:1, 1:8, 8:1
    - 512px (0.5K) resolution option
    - Google Image Search grounding
    """

    def __init__(self):
        self.client = None
        self.last_image_data = None
        self.conversation_history = []
        self.current_approach = None
        self.current_model_name = None
        self.current_aspect_ratio = None
        self.current_image_size = None
        self.current_temperature = None
        self._preview_warning_shown = False

    @classmethod
    def INPUT_TYPES(s):
        model_list = ["gemini-3.1-flash-image", "gemini-3.1-flash-image-preview"]
        return {
            "required": {
                "model_name": (model_list, {"default": model_list[0]}),
                "prompt": ("STRING", {"multiline": True, "default": "Create an image of a clear perfume bottle sitting on a vanity."}),
                "reset_chat": ("BOOLEAN", {"default": False}),
                "use_search": ("BOOLEAN", {"default": False}),
                "use_image_search": ("BOOLEAN", {"default": False}),
                "thinking_level": (["minimal", "high"], {"default": "minimal"}),
                "include_thoughts": ("BOOLEAN", {"default": False}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2147483647, "control_after_generate": True}),
                "aspect_ratio": (["1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9", "Auto"], {"default": "1:1"}),
                "image_size": (["512px", "1K", "2K", "4K"], {"default": "2K"}),
                "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
            },
            "optional": {
                "image_1": ("IMAGE",), "image_2": ("IMAGE",), "image_3": ("IMAGE",),
                "image_4": ("IMAGE",), "image_5": ("IMAGE",), "image_6": ("IMAGE",),
                "image_7": ("IMAGE",), "image_8": ("IMAGE",), "image_9": ("IMAGE",),
                "image_10": ("IMAGE",), "image_11": ("IMAGE",), "image_12": ("IMAGE",),
                "image_13": ("IMAGE",), "image_14": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING", "STRING", "STRING", "IMAGE")
    RETURN_NAMES = ("image", "response_text", "metadata", "chat_history", "thinking", "thought_images")

    FUNCTION = "generate_multiturn_image"
    CATEGORY = "Ru4ls/NanoBanana"

    def _handle_error(self, message):
        print(f"\033[91mERROR: {message}\033[0m")
        return (torch.zeros(1, 64, 64, 3), "", "", "", "", torch.zeros(1, 64, 64, 3))

    def _create_config(self, aspect_ratio, image_size, temperature, use_search, use_image_search, model_name, thinking_level, include_thoughts, seed):
        """Centralized config creation with proper AFC handling and Image Search support."""
        if "preview" in model_name and not self._preview_warning_shown:
            print(f"Warning: Using preview model {model_name} which may have unstable tool support")
            self._preview_warning_shown = True

        image_config_kwargs = {
            "image_size": image_size
        }

        if aspect_ratio != "Auto":
            image_config_kwargs["aspect_ratio"] = aspect_ratio

        config_kwargs = {
            "response_modalities": ["TEXT", "IMAGE"],
            "image_config": types.ImageConfig(**image_config_kwargs),
            "temperature": temperature,
            "seed": seed,
            "thinking_config": types.ThinkingConfig(
                thinking_level=thinking_level,
                include_thoughts=include_thoughts,
            ),
            "automatic_function_calling": types.AutomaticFunctionCallingConfig(disable=True)
        }

        if use_search:
            try:
                if use_image_search:
                    config_kwargs["tools"] = [{
                        "google_search": {
                            "search_types": {
                                "web_search": {},
                                "image_search": {}
                            }
                        }
                    }]
                    print("Info: Using Google Image Search grounding")
                else:
                    config_kwargs["tools"] = [{"google_search": {}}]
                    print("Info: Using Google Web Search grounding")
            except Exception as e:
                print(f"Warning: Search tool configuration failed: {e}")
                print("Info: Falling back to basic search or no search")
                pass
        else:
            print("Info: Search grounding disabled")

        config = types.GenerateContentConfig(**config_kwargs)
        return config

    def _response_parts(self, response):
        """Separate final response parts from thought parts."""
        final_image_bytes = None
        response_text_parts = []
        thought_text_parts = []
        thought_image_bytes = []

        for part in response.candidates[0].content.parts:
            is_thought = bool(getattr(part, "thought", False))
            inline_data = getattr(part, "inline_data", None)
            text = getattr(part, "text", None)

            if inline_data:
                if is_thought:
                    thought_image_bytes.append(inline_data.data)
                elif final_image_bytes is None:
                    final_image_bytes = inline_data.data

            if text:
                if is_thought:
                    thought_text_parts.append(text)
                else:
                    response_text_parts.append(text)

        return {
            "final_image_bytes": final_image_bytes,
            "response_text": "".join(response_text_parts),
            "thought_text": "".join(thought_text_parts),
            "thought_image_bytes": thought_image_bytes,
        }

    def _image_bytes_to_tensor(self, image_bytes):
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_np = np.array(pil_image).astype(np.float32) / 255.0
        return torch.from_numpy(image_np)[None,]

    def _image_bytes_list_to_tensor(self, image_bytes_list):
        tensors = [self._image_bytes_to_tensor(image_bytes) for image_bytes in image_bytes_list]
        if tensors:
            return torch.cat(tensors, dim=0)
        return torch.zeros(1, 64, 64, 3)

    def _create_client(self, approach, model_name):
        """Create a new client based on the approach."""
        if approach == "VERTEXAI":
            if not PROJECT_ID or not LOCATION:
                raise ValueError("PROJECT_ID or LOCATION not configured in .env for Vertex AI approach")

            location = "global" if "gemini-3" in model_name else LOCATION
            client = genai.Client(vertexai=True, project=PROJECT_ID, location=location)
        else:
            if not GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY not configured in .env for API approach")

            client = genai.Client(api_key=GOOGLE_API_KEY)

        return client

    def generate_multiturn_image(self, model_name, prompt, reset_chat=False, use_search=False, use_image_search=False,
                                  thinking_level="minimal", include_thoughts=False, seed=0,
                                  aspect_ratio="1:1", image_size="2K", temperature=1.0,
                                  image_1=None, image_2=None, image_3=None, image_4=None, image_5=None,
                                  image_6=None, image_7=None, image_8=None, image_9=None, image_10=None,
                                  image_11=None, image_12=None, image_13=None, image_14=None):
        try:
            approach = detect_approach()

            if not prompt or prompt.strip() == "":
                return self._handle_error("Prompt cannot be empty")

            if not model_name:
                return self._handle_error("Model name is required")

            valid_thinking_levels = ["minimal", "high"]
            if thinking_level not in valid_thinking_levels:
                return self._handle_error(f"Invalid thinking level. Valid options: {', '.join(valid_thinking_levels)}")

            if seed < 0 or seed > 2147483647:
                return self._handle_error("Seed must be between 0 and 2147483647")

            # Validate aspect ratio
            valid_ratios = ["1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9", "Auto"]
            if aspect_ratio not in valid_ratios:
                return self._handle_error(f"Invalid aspect ratio. Valid options: {', '.join(valid_ratios)}")

            # Validate image_size
            valid_sizes = ["512px", "1K", "2K", "4K"]
            if image_size not in valid_sizes:
                return self._handle_error(f"Invalid image size. Valid options: {', '.join(valid_sizes)}")

            # Reset chat session if requested
            if reset_chat:
                self.last_image_data = None
                self.conversation_history = []
                print("Chat session reset.")

            # Create client for this request
            client = self._create_client(approach, model_name)

            # Prepare content for the chat message
            contents = [prompt]

            # Collect reference images
            reference_images = [image_1, image_2, image_3, image_4, image_5, image_6,
                               image_7, image_8, image_9, image_10, image_11, image_12,
                               image_13, image_14]
            
            image_count_provided = 0
            for img_tensor in reference_images:
                if img_tensor is not None:
                    contents.append(tensor_to_pil(img_tensor))
                    image_count_provided += 1

            if image_count_provided > 14:
                return self._handle_error("Maximum 14 reference images supported")

            # If this is the first message and reference images are provided, include them
            if len(self.conversation_history) == 0 and image_count_provided > 0:
                print(f"Info: Starting conversation with {image_count_provided} reference image(s)")
            # If we have a previous image from the conversation, include it
            elif self.last_image_data is not None:
                prev_image = Image.open(io.BytesIO(self.last_image_data))
                contents.insert(0, prev_image)

            # Create config
            config = self._create_config(aspect_ratio, image_size, temperature, use_search, use_image_search, model_name, thinking_level, include_thoughts, seed)

            # Create the chat session
            chat = client.chats.create(
                model=model_name,
                config=config
            )

            response = chat.send_message(message=contents)

            # Validate response and check finish reason
            if not response.candidates:
                return self._handle_error("API returned no candidates.")

            if hasattr(response.candidates[0], 'finish_reason') and response.candidates[0].finish_reason != types.FinishReason.STOP:
                reason = response.candidates[0].finish_reason
                print(f"Debug: Full response - {response}")
                if hasattr(response, 'candidates') and response.candidates:
                    print(f"Debug: Candidates - {response.candidates[0]}")
                    if hasattr(response.candidates[0], 'content'):
                        print(f"Debug: Parts - {response.candidates[0].content.parts}")
                return self._handle_error(f"Generation failed with reason: {reason}")

            # Parse the response
            parts = self._response_parts(response)
            image_bytes = parts["final_image_bytes"]
            text_response = parts["response_text"]
            thinking = parts["thought_text"]
            thought_images = self._image_bytes_list_to_tensor(parts["thought_image_bytes"])

            if image_bytes is None:
                print(f"Debug: Full response - {response}")
                print(f"Debug: Response parts - {response.candidates[0].content.parts}")
                print(f"Debug: Text response - {text_response[:500] if text_response else 'None'}")
                print(f"Debug: Thinking response - {thinking[:500] if thinking else 'None'}")
                return self._handle_error("No image data found in the API response.")

            # Update the stored image data for next turn
            self.last_image_data = image_bytes

            # Update conversation history
            self.conversation_history.append({
                "prompt": prompt,
                "response": text_response if text_response else "Image generated"
            })

            # Convert image to tensor
            image_tensor = self._image_bytes_to_tensor(image_bytes)

            # Extract metadata
            metadata = self._extract_metadata(response)

            # Convert conversation history to a string representation
            chat_history_str = str(self.conversation_history)

            return (image_tensor, text_response, metadata, chat_history_str, thinking, thought_images)

        except ValueError as e:
            return self._handle_error(f"ValueError in NanoBanana2MultiTurnChat: {e}")
        except TypeError as e:
            return self._handle_error(f"TypeError in NanoBanana2MultiTurnChat: {e}")
        except Exception as e:
            return self._handle_error(f"{type(e).__name__} in NanoBanana2MultiTurnChat: {e}")

    def _extract_metadata(self, response):
        """Extract any relevant metadata from the response."""
        try:
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                metadata = f"Finish Reason: {candidate.finish_reason}"

                if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                    safety_info = [f"{rating.category.name}: {rating.harm_probability.name}"
                                  for rating in candidate.safety_ratings]
                    if safety_info:
                        metadata += f"\nSafety Ratings: {', '.join(safety_info)}"

                return metadata
            else:
                return "No metadata available"
        except Exception as e:
            return f"Metadata extraction error: {str(e)}"
