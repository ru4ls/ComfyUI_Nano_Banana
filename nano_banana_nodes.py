import os
import io
import torch
import numpy as np

from PIL import Image
from dotenv import load_dotenv

from google import genai
from google.genai import types

# Load environment variables from a .env file
load_dotenv()

# --- Utility Function ---
def image_to_pil(image_tensor):
    """Convert a PyTorch tensor to PIL Image"""
    return Image.fromarray((image_tensor[0].cpu().numpy() * 255.).astype(np.uint8))

class NanoBanana:
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

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_image"
    CATEGORY = "Ru4ls/NanoBanana"

    def generate_image(self, model_name, prompt, image_1=None, image_2=None, image_3=None, image_4=None, image_5=None, image_6=None, aspect_ratio="1:1", image_size="2K", temperature=1.0):
        try:
            # --- 1. Initialize the Client with an API Key ---
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise Exception("GOOGLE_API_KEY not found in .env file.")
            
            client = genai.Client(api_key=api_key)

            # --- 2. Prepare Contents ---
            contents = [prompt]
            images = [image_1, image_2, image_3, image_4, image_5, image_6]  # Up to 6 images as per update documentation
            for img_tensor in images:
                if img_tensor is not None:
                    contents.append(image_to_pil(img_tensor))

            # --- 3. Create the Full Configuration ---
            config = types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=image_size
                ),
                temperature=temperature
            )
            
            # --- 4. Call the Correct, Unified Method ---
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )

            # --- 5. Validate response and check finish reason ---
            if not response.candidates:
                raise Exception("API returned no candidates.")

            # Check if generation was successful
            if response.candidates[0].finish_reason != types.FinishReason.STOP:
                reason = response.candidates[0].finish_reason
                raise Exception(f"Generation failed with reason: {reason}")

            # --- 6. Parse the Response ---
            image_bytes = None

            for part in response.candidates[0].content.parts:
                if part.inline_data and image_bytes is None:
                    image_bytes = part.inline_data.data
                    break

            if image_bytes is None:
                raise Exception("No image data found in the API response.")

            pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            image_np = np.array(pil_image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_np)[None,]

            return (image_tensor,)

        except Exception as e:
            raise Exception(f"An error occurred in NanoBananaAPIKeyNode: {type(e).__name__} - {e}")