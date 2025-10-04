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
        model_list = ["gemini-2.5-flash-image", "gemini-2.5-flash-image-preview"]
        return {
            "required": {
                "model_name": (model_list, {"default": model_list[0]}),
                "prompt": ("STRING", {"multiline": True, "default": "A futuristic nano banana dish"}),
            },
            "optional": {
                "image_1": ("IMAGE",), "image_2": ("IMAGE",), "image_3": ("IMAGE",),
                "aspect_ratio": (["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"], {"default": "1:1"}),
                "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_image"
    CATEGORY = "Ru4ls/NanoBanana"

    def generate_image(self, model_name, prompt, image_1=None, image_2=None, image_3=None, aspect_ratio="1:1", temperature=1.0):
        try:
            # --- 1. Initialize the Client with an API Key ---
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise Exception("GOOGLE_API_KEY not found in .env file.")
            
            client = genai.Client(api_key=api_key)

            # --- 2. Prepare Contents ---
            contents = [prompt]
            images = [image_1, image_2, image_3]
            for img_tensor in images:
                if img_tensor is not None:
                    contents.append(image_to_pil(img_tensor))

            # --- 3. Create the Full Configuration ---
            config = types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
                temperature=temperature
            )
            
            # --- 4. Call the Correct, Unified Method ---
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            
            # --- 5. Parse the Response (Same robust parsing) ---
            if not response.candidates:
                raise Exception("API returned no candidates.")

            image_bytes = None
            for part in response.candidates[0].content.parts:
                if part.inline_data:
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