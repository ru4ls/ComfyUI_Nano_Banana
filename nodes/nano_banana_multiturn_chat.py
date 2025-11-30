import io, torch, numpy as np
from PIL import Image

from google import genai
from google.genai import types

from ..core.auth import detect_approach, PROJECT_ID, LOCATION, GOOGLE_API_KEY
from ..utils.image_utils import tensor_to_pil

class NanoBananaMultiTurnChat:
    """
    A multimodal node that supports multi-turn chat-based image generation and editing.
    Maintains conversation history and allows iterative image modifications.
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
        self._preview_warning_shown = False  # Track if warning was shown

    @classmethod
    def INPUT_TYPES(s):
        model_list = ["gemini-3-pro-image-preview"]
        return {
            "required": {
                "model_name": (model_list, {"default": model_list[0]}),
                "prompt": ("STRING", {"multiline": True, "default": "Create an image of a clear perfume bottle sitting on a vanity."}),
                "reset_chat": ("BOOLEAN", {"default": False}),
                "aspect_ratio": (["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"], {"default": "1:1"}),
                "image_size": (["1K", "2K", "4K"], {"default": "2K"}),
                "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
            },
            "optional": {
                "image_input": ("IMAGE",),  # Optional: Initial image to start the conversation with
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("image", "response_text", "metadata", "chat_history")

    FUNCTION = "generate_multiturn_image"
    CATEGORY = "Ru4ls/NanoBanana"

    def _handle_error(self, message):
        print(f"\033[91mERROR: {message}\033[0m")
        # Always return the same number of outputs to maintain ComfyUI compatibility
        return (torch.zeros(1, 64, 64, 3), "", "", [])

    def generate_multiturn_image(self, model_name, prompt, reset_chat=False, aspect_ratio="1:1", image_size="2K", temperature=1.0, image_input=None):
        try:
            approach = detect_approach()

            if not prompt or prompt.strip() == "":
                return self._handle_error("Prompt cannot be empty")

            if not model_name:
                return self._handle_error("Model name is required")

            # Validate aspect ratio
            valid_ratios = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]
            if aspect_ratio not in valid_ratios:
                return self._handle_error(f"Invalid aspect ratio. Valid options: {', '.join(valid_ratios)}")

            # Validate image_size
            valid_sizes = ["1K", "2K", "4K"]
            if image_size not in valid_sizes:
                return self._handle_error(f"Invalid image size. Valid options: {', '.join(valid_sizes)}")

            # Reset chat session if requested
            if reset_chat:
                self.last_image_data = None
                self.conversation_history = []
                print("Chat session reset.")

            # Show warning for preview models
            if "preview" in model_name and not self._preview_warning_shown:
                print(f"Warning: Using preview model {model_name} which may have unstable tool support")
                self._preview_warning_shown = True

            # Create client for this request
            client = self._create_client(approach, model_name)

            # Prepare content for the chat message
            contents = [prompt]

            # If this is the first message and an initial image is provided, include it
            if len(self.conversation_history) == 0 and image_input is not None:
                pil_image = tensor_to_pil(image_input)
                contents.insert(0, pil_image)
            # If we have a previous image from the conversation, include it
            elif self.last_image_data is not None:
                # Convert the stored image bytes to a format the API can use
                prev_image = Image.open(io.BytesIO(self.last_image_data))
                contents.insert(0, prev_image)

            # Create the chat session with configuration for this request
            config = types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=image_size
                ),
                temperature=temperature,
                # FIX: Disable AFC to prevent malformed function calls
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            )

            # Create and send message in a fresh chat session
            chat = client.chats.create(
                model=model_name,
                config=config
            )

            response = chat.send_message(
                message=contents
            )

            # Validate response and check finish reason
            if not response.candidates:
                return self._handle_error("API returned no candidates.")

            # Check if generation was successful
            if hasattr(response.candidates[0], 'finish_reason') and response.candidates[0].finish_reason != types.FinishReason.STOP:
                reason = response.candidates[0].finish_reason
                # Add debug information
                print(f"Debug: Full response - {response}")
                if hasattr(response, 'candidates') and response.candidates:
                    print(f"Debug: Candidates - {response.candidates[0]}")
                    if hasattr(response.candidates[0], 'content'):
                        print(f"Debug: Parts - {response.candidates[0].content.parts}")
                return self._handle_error(f"Generation failed with reason: {reason}")

            # Parse the response
            image_bytes = None
            text_response = ""

            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data and image_bytes is None:
                    image_bytes = part.inline_data.data
                elif hasattr(part, 'text') and part.text:
                    text_response += part.text

            if image_bytes is None:
                return self._handle_error("No image data found in the API response.")

            # Update the stored image data for next turn
            self.last_image_data = image_bytes

            # Update conversation history
            self.conversation_history.append({
                "prompt": prompt,
                "response": text_response if text_response else "Image generated"
            })

            # Convert image to tensor
            pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            image_np = np.array(pil_image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_np)[None,]

            # Extract any metadata from the response
            metadata = self._extract_metadata(response)

            # Convert conversation history to a string representation
            chat_history_str = str(self.conversation_history)

            return (image_tensor, text_response, metadata, chat_history_str)

        except ValueError as e:
            return self._handle_error(f"ValueError in NanoBananaMultiTurnChat: {e}")
        except TypeError as e:
            return self._handle_error(f"TypeError in NanoBananaMultiTurnChat: {e}")
        except Exception as e:
            return self._handle_error(f"{type(e).__name__} in NanoBananaMultiTurnChat: {e}")

    def _create_client(self, approach, model_name):
        """Create a new client based on the approach."""
        if approach == "VERTEXAI":
            if not PROJECT_ID or not LOCATION:
                raise ValueError("PROJECT_ID or LOCATION not configured in .env for Vertex AI approach")

            # Use global location for nanobanana models as they may only be available on global endpoint
            location = "global" if "gemini-3-pro" in model_name else LOCATION
            client = genai.Client(
                vertexai=True,
                project=PROJECT_ID,
                location=location
            )
        else:  # API approach
            if not GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY not configured in .env for API approach")

            client = genai.Client(
                api_key=GOOGLE_API_KEY
            )

        return client

    def _extract_metadata(self, response):
        """Extract any relevant metadata from the response."""
        try:
            # Check for finish reason or other metadata
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                metadata = f"Finish Reason: {candidate.finish_reason}"

                # Add any safety ratings if available
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