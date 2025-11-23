import io, torch, numpy as np
from PIL import Image

from google import genai
from google.genai import types

from ..core.auth import detect_approach, PROJECT_ID, LOCATION, GOOGLE_API_KEY
from ..utils.image_utils import tensor_to_pil

class NanoBanana:
    """A multimodal node supporting both Vertex AI and Google Generative AI API approaches."""
    def __init__(self):
        self.client = None

    @classmethod
    def INPUT_TYPES(s):
        model_list = ["gemini-3-pro-image-preview"]
        return {
            "required": {
                "model_name": (model_list, {"default": model_list[0]}),
                "prompt": ("STRING", {"multiline": True, "default": "A futuristic nano banana dish"}),
            },
            "optional": {
                "image_1": ("IMAGE",), "image_2": ("IMAGE",), "image_3": ("IMAGE",),
                "image_4": ("IMAGE",), "image_5": ("IMAGE",), "image_6": ("IMAGE",),
                "aspect_ratio": (["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"], {"default": "1:1"}),
                "image_size": (["1K", "2K", "4K"], {"default": "2K"}),
                "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "thinking")
    FUNCTION = "generate_image"
    CATEGORY = "Ru4ls/NanoBanana"

    def _handle_error(self, message):
        print(f"\033[91mERROR: {message}\033[0m")
        return (torch.zeros(1, 64, 64, 3), "")

    def generate_image(self, model_name, prompt, image_1=None, image_2=None, image_3=None, image_4=None, image_5=None, image_6=None, aspect_ratio="1:1", image_size="2K", temperature=1.0):
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

            # Prepare contents
            contents = [prompt]
            images = [image_1, image_2, image_3, image_4, image_5, image_6]
            for img_tensor in images:
                if img_tensor is not None:
                    contents.append(tensor_to_pil(img_tensor))

            # Use different configuration based on approach
            if approach == "VERTEXAI":
                if not PROJECT_ID or not LOCATION:
                    return self._handle_error("PROJECT_ID or LOCATION not configured in .env for Vertex AI approach")

                # Use global location for nanobanana models as they may only be available on global endpoint
                location = "global" if "gemini-3-pro" in model_name else LOCATION
                client = genai.Client(vertexai=True, project=PROJECT_ID, location=location)

                # For Vertex AI, request both image and text to capture thinking
                config = types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    image_config=types.ImageConfig(aspect_ratio=aspect_ratio, image_size=image_size),
                    temperature=temperature
                )
            else:  # API approach
                if not GOOGLE_API_KEY:
                    return self._handle_error("GOOGLE_API_KEY not configured in .env for API approach")

                client = genai.Client(api_key=GOOGLE_API_KEY)

                # For API approach, request only image
                config = types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(aspect_ratio=aspect_ratio, image_size=image_size),
                    temperature=temperature
                )

            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )

            # Validate response and check finish reason
            if not response.candidates:
                return self._handle_error("API returned no candidates.")

            # Check if generation was successful
            if hasattr(response.candidates[0], 'finish_reason') and response.candidates[0].finish_reason != types.FinishReason.STOP:
                reason = response.candidates[0].finish_reason
                return self._handle_error(f"Generation failed with reason: {reason}")

            # Parse the response to extract image and potentially text (thinking)
            image_bytes = None
            thinking = ""

            for part in response.candidates[0].content.parts:
                if part.inline_data and image_bytes is None:
                    image_bytes = part.inline_data.data
                elif part.text:
                    thinking += part.text

            if image_bytes is None:
                return self._handle_error("No image data found in the API response.")

            pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            output_image = np.array(pil_image).astype(np.float32) / 255.0
            output_tensor = torch.from_numpy(output_image)[None,]

            # For API approach, provide a helpful message about needing Vertex AI for thinking output
            if approach == "API":
                thinking = "To access the thinking/thought process, please use Vertex AI approach with PROJECT_ID and LOCATION configured.\nVisit https://cloud.google.com/vertex-ai/docs/generative-ai/learn/quickstarts for setup instructions."

            return (output_tensor, thinking)

        except ValueError as e:
            return self._handle_error(f"ValueError in NanoBanana: {e}")
        except TypeError as e:
            return self._handle_error(f"TypeError in NanoBanana: {e}")
        except Exception as e:
            return self._handle_error(f"{type(e).__name__} in NanoBanana: {e}")