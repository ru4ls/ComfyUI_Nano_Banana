import torch
import numpy as np
from PIL import Image
import requests
import base64
import io
import os
from dotenv import load_dotenv

load_dotenv()

def image_to_base64(image_tensor):
    image_pil = Image.fromarray((image_tensor[0].cpu().numpy() * 255.).astype(np.uint8)).convert("RGB")
    buffered = io.BytesIO()
    image_pil.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

class NanoBanana:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
            },
            "optional": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "width": ("INT", {"default": 1024, "min": 64, "max": 4096, "step": 64}),
                "height": ("INT", {"default": 1024, "min": 64, "max": 4096, "step": 64}),
                "image_1": ("IMAGE",),
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "image_4": ("IMAGE",),
                "image_5": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_image"
    CATEGORY = "Gemini/NanoBanana"

    def generate_image(self, prompt, seed=0, width=1024, height=1024,
                       image_1=None, image_2=None, image_3=None, image_4=None, image_5=None):
        api_key = os.getenv("REPLICATE_API_KEY")
        if not api_key:
            raise Exception("API key not found in .env file.")

        url = os.getenv("URL_ENDPOINT", "https://generativelanguage.googleapis.com/v1alpha/models/gemini-2.5-flash-image-preview:generateContent")

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }

        parts = [{"text": prompt}]

        images = [image_1, image_2, image_3, image_4, image_5]
        for img_tensor in images:
            if img_tensor is not None:
                image_b64 = image_to_base64(img_tensor)
                parts.append({
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": image_b64
                    }
                })

        data = {"contents": [{"parts": parts}]}

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            if 'candidates' not in result or not result['candidates']:
                raise Exception("No candidates found in API response")

            parts = result['candidates'][0]['content']['parts']
            for part in parts:
                if 'inlineData' in part:
                    image_data_b64 = part['inlineData']['data']
                    image_data = base64.b64decode(image_data_b64)
                    image = Image.open(io.BytesIO(image_data)).convert("RGB")
                    
                    image = np.array(image).astype(np.float32) / 255.0
                    image = torch.from_numpy(image)[None,]
                    
                    return (image,)
            
            raise Exception("No image data found in API response")

        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to parse API response: {e}")
        except Exception as e:
            raise Exception(f"An error occurred: {e}")