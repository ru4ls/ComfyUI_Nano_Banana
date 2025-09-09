import torch
import numpy as np
from PIL import Image
import requests
import base64
import io
import json
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

class NanoBananaTextToImage:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "width": ("INT", {"default": 1024, "min": 64, "max": 4096, "step": 64}),
                "height": ("INT", {"default": 1024, "min": 64, "max": 4096, "step": 64}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_image"
    CATEGORY = "Gemini/NanoBanana"

    def generate_image(self, prompt, seed, width, height):
        config = load_config()
        api_key = config.get("api_key")
        if not api_key:
            raise Exception("API key not found in config.json file.")

        url = config.get("url_endpoint", "https://generativelanguage.googleapis.com/v1alpha/models/gemini-2.5-flash-image-preview:generateContent")

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

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

class NanoBananaImageToImage:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_image"
    CATEGORY = "Gemini/NanoBanana"

    def generate_image(self, prompt, image):
        config = load_config()
        api_key = config.get("api_key")
        if not api_key:
            raise Exception("API key not found in config.json file.")

        url = config.get("url_endpoint", "https://generativelanguage.googleapis.com/v1alpha/models/gemini-2.5-flash-image-preview:generateContent")

        image_pil = Image.fromarray((image[0].cpu().numpy() * 255.).astype(np.uint8)).convert("RGB")
        buffered = io.BytesIO()
        image_pil.save(buffered, format="PNG")
        image_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": image_b64
                            }
                        }
                    ]
                }
            ]
        }

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
                    new_image = Image.open(io.BytesIO(image_data)).convert("RGB")

                    new_image = np.array(new_image).astype(np.float32) / 255.0
                    new_image = torch.from_numpy(new_image)[None,]

                    return (new_image,)

            raise Exception("No image data found in API response")

        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to parse API response: {e}")
        except Exception as e:
            raise Exception(f"An error occurred: {e}")

class NanoBananaMultiImageToImage:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "image1": ("IMAGE",),
            },
            "optional": {
                "image2": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_image"
    CATEGORY = "Gemini/NanoBanana"

    def generate_image(self, prompt, image1, image2=None):
        config = load_config()
        api_key = config.get("api_key")
        if not api_key:
            raise Exception("API key not found in config.json file.")

        url = config.get("url_endpoint", "https://generativelanguage.googleapis.com/v1alpha/models/gemini-2.5-flash-image-preview:generateContent")

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }

        parts = [{"text": prompt}]
        
        images = [image1]
        if image2 is not None:
            images.append(image2)

        for image_tensor in images:
            image_pil = Image.fromarray((image_tensor[0].cpu().numpy() * 255.).astype(np.uint8)).convert("RGB")
            buffered = io.BytesIO()
            image_pil.save(buffered, format="PNG")
            image_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
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
                    new_image = Image.open(io.BytesIO(image_data)).convert("RGB")

                    new_image = np.array(new_image).astype(np.float32) / 255.0
                    new_image = torch.from_numpy(new_image)[None,]

                    return (new_image,)

            raise Exception("No image data found in API response")

        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to parse API response: {e}")
        except Exception as e:
            raise Exception(f"An error occurred: {e}")