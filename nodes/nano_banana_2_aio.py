import io, torch, numpy as np
from PIL import Image

from google import genai
from google.genai import types

from ..core.auth import detect_approach, PROJECT_ID, LOCATION, GOOGLE_API_KEY
from ..utils.image_utils import tensor_to_pil

class NanoBanana2AIO:
    """
    Nano Banana 2 AIO node using gemini-3.1-flash-image model.
    Optimized for speed and high-volume use cases with support for:
    - Up to 14 reference images (10 objects + 4 characters)
    - New aspect ratios: 1:4, 4:1, 1:8, 8:1
    - 512px (0.5K) resolution option
    - Google Image Search grounding
    """
    def __init__(self):
        self.client = None
        self._preview_warning_shown = False

    @classmethod
    def INPUT_TYPES(s):
        model_list = ["gemini-3.1-flash-image", "gemini-3.1-flash-image-preview"]
        return {
            "required": {
                "model_name": (model_list, {"default": model_list[0]}),
                "prompt": ("STRING", {"multiline": True, "default": "A futuristic nano banana dish"}),
                "image_count": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1}),
                "use_search": ("BOOLEAN", {"default": False}),
                "use_image_search": ("BOOLEAN", {"default": False}),
                "thinking_level": (["minimal", "high"], {"default": "minimal"}),
                "include_thoughts": ("BOOLEAN", {"default": False}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2147483647, "control_after_generate": True}),
            },
            "optional": {
                "image_1": ("IMAGE",), "image_2": ("IMAGE",), "image_3": ("IMAGE",),
                "image_4": ("IMAGE",), "image_5": ("IMAGE",), "image_6": ("IMAGE",),
                "image_7": ("IMAGE",), "image_8": ("IMAGE",), "image_9": ("IMAGE",),
                "image_10": ("IMAGE",), "image_11": ("IMAGE",), "image_12": ("IMAGE",),
                "image_13": ("IMAGE",), "image_14": ("IMAGE",),
                "aspect_ratio": (["1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9", "Auto"], {"default": "1:1"}),
                "image_size": (["512px", "1K", "2K", "4K"], {"default": "2K"}),
                "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING", "IMAGE")
    RETURN_NAMES = ("images", "thinking", "grounding_sources", "thought_images")

    FUNCTION = "generate_unified"
    CATEGORY = "Ru4ls/NanoBanana"

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
                    # Use dictionary format for Image Search grounding
                    # Note: This requires the latest google-genai SDK
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
                    # Use dictionary format for Web Search grounding
                    config_kwargs["tools"] = [{"google_search": {}}]
                    print("Info: Using Google Web Search grounding")
            except Exception as e:
                print(f"Warning: Search tool configuration failed: {e}")
                print("Info: Falling back to basic search or no search")
                # Don't set tools if configuration fails
                pass
        else:
            print("Info: Search grounding disabled")

        config = types.GenerateContentConfig(**config_kwargs)
        return config

    def _handle_error(self, message):
        print(f"\033[91mERROR: {message}\033[0m")
        return (torch.zeros(1, 64, 64, 3), "", "", torch.zeros(1, 64, 64, 3))

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

    def generate_unified(self, model_name, prompt, image_count=1, use_search=True, use_image_search=False, 
                         thinking_level="minimal", include_thoughts=False, seed=0,
                         image_1=None, image_2=None, image_3=None, image_4=None, image_5=None, 
                         image_6=None, image_7=None, image_8=None, image_9=None, image_10=None,
                         image_11=None, image_12=None, image_13=None, image_14=None, 
                         aspect_ratio="1:1", image_size="2K", temperature=1.0):
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

            if image_count < 1 or image_count > 10:
                return self._handle_error("Image count must be between 1 and 10")

            valid_ratios = ["1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9", "Auto"]
            if aspect_ratio not in valid_ratios:
                return self._handle_error(f"Invalid aspect ratio. Valid options: {', '.join(valid_ratios)}")

            valid_sizes = ["512px", "1K", "2K", "4K"]
            if image_size not in valid_sizes:
                return self._handle_error(f"Invalid image size. Valid options: {', '.join(valid_sizes)}")

            contents = [prompt]
            images = [image_1, image_2, image_3, image_4, image_5, image_6, 
                      image_7, image_8, image_9, image_10, image_11, image_12, 
                      image_13, image_14]
            
            image_count_provided = 0
            for img_tensor in images:
                if img_tensor is not None:
                    contents.append(tensor_to_pil(img_tensor))
                    image_count_provided += 1

            if image_count_provided > 14:
                return self._handle_error("Maximum 14 reference images supported")

            if image_count == 1:
                return self._generate_single_image(
                    model_name, prompt, use_search, use_image_search, approach, contents,
                    aspect_ratio, image_size, temperature, thinking_level, include_thoughts, seed
                )
            else:
                return self._generate_multiple_images(
                    model_name, prompt, image_count, use_search, use_image_search, approach, contents,
                    aspect_ratio, image_size, temperature, thinking_level, include_thoughts, seed
                )

        except ValueError as e:
            return self._handle_error(f"ValueError in NanoBanana2AIO: {e}")
        except TypeError as e:
            return self._handle_error(f"TypeError in NanoBanana2AIO: {e}")
        except Exception as e:
            return self._handle_error(f"{type(e).__name__} in NanoBanana2AIO: {e}")

    def _generate_single_image(self, model_name, prompt, use_search, use_image_search, approach, contents, aspect_ratio, image_size, temperature, thinking_level, include_thoughts, seed):
        """Generate a single image with grounding capabilities."""
        if approach == "VERTEXAI":
            if not PROJECT_ID or not LOCATION:
                return self._handle_error("PROJECT_ID or LOCATION not configured in .env for Vertex AI approach")

            location = "global" if "gemini-3" in model_name else LOCATION
            client = genai.Client(vertexai=True, project=PROJECT_ID, location=location)
        else:
            if not GOOGLE_API_KEY:
                return self._handle_error("GOOGLE_API_KEY not configured in .env for API approach")

            client = genai.Client(api_key=GOOGLE_API_KEY)

        config = self._create_config(aspect_ratio, image_size, temperature, use_search, use_image_search, model_name, thinking_level, include_thoughts, seed)

        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config
        )

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

        parts = self._response_parts(response)
        image_bytes = parts["final_image_bytes"]
        text_response = parts["response_text"]
        thinking = parts["thought_text"]
        thought_images = self._image_bytes_list_to_tensor(parts["thought_image_bytes"])

        grounding_sources = self.extract_grounding_data(response)

        if image_bytes is None:
            # Debug: print response parts to help diagnose the issue
            print(f"Debug: Full response - {response}")
            print(f"Debug: Response parts - {response.candidates[0].content.parts}")
            print(f"Debug: Text response - {text_response[:500] if text_response else 'None'}")
            print(f"Debug: Thinking response - {thinking[:500] if thinking else 'None'}")
            if grounding_sources:
                print(f"Debug: Grounding sources - {grounding_sources[:500] if grounding_sources else 'None'}")
            return self._handle_error("No image data found in the API response.")

        image_tensor = self._image_bytes_to_tensor(image_bytes)

        return (image_tensor, thinking, grounding_sources, thought_images)

    def _generate_multiple_images(self, model_name, prompt, image_count, use_search, use_image_search, approach, contents, aspect_ratio, image_size, temperature, thinking_level, include_thoughts, seed):
        """Generate multiple images with grounding capabilities."""
        generated_images = []
        all_thinking_responses = []
        all_grounding_sources = []
        all_thought_image_bytes = []

        for i in range(image_count):
            current_prompt = f"{prompt} (Image {i+1} of {image_count})"
            current_contents = [current_prompt] + contents[1:]

            if approach == "VERTEXAI":
                if not PROJECT_ID or not LOCATION:
                    return self._handle_error("PROJECT_ID or LOCATION not configured in .env for Vertex AI approach")

                location = "global" if "gemini-3" in model_name else LOCATION
                client = genai.Client(vertexai=True, project=PROJECT_ID, location=location)
            else:
                if not GOOGLE_API_KEY:
                    return self._handle_error("GOOGLE_API_KEY not configured in .env for API approach")

                client = genai.Client(api_key=GOOGLE_API_KEY)

            config = self._create_config(aspect_ratio, image_size, temperature, use_search, use_image_search, model_name, thinking_level, include_thoughts, seed)

            response = client.models.generate_content(
                model=model_name,
                contents=current_contents,
                config=config
            )

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

            parts = self._response_parts(response)
            image_bytes = parts["final_image_bytes"]
            text_response = parts["response_text"]
            thinking = parts["thought_text"]
            all_thought_image_bytes.extend(parts["thought_image_bytes"])

            grounding_sources = self.extract_grounding_data(response)

            if image_bytes is None:
                # Debug: print response parts to help diagnose the issue
                print(f"Debug: Response parts - {response.candidates[0].content.parts}")
                print(f"Debug: Text response - {text_response[:500] if text_response else 'None'}")
                print(f"Debug: Thinking response - {thinking[:500] if thinking else 'None'}")
                return self._handle_error("No image data found in the API response.")

            image_tensor = self._image_bytes_to_tensor(image_bytes)

            generated_images.append(image_tensor)
            all_thinking_responses.append(thinking)
            all_grounding_sources.append(grounding_sources)

        if len(generated_images) > 0:
            combined_images = torch.cat(generated_images, dim=0)
        else:
            return self._handle_error("No images were generated.")

        combined_thinking_responses = "\n\n".join(all_thinking_responses)
        combined_grounding_sources = "\n\n".join(all_grounding_sources)
        thought_images = self._image_bytes_list_to_tensor(all_thought_image_bytes)

        return (combined_images, combined_thinking_responses, combined_grounding_sources, thought_images)

    def extract_grounding_data(self, response):
        """Extracts grounding sources from the response."""
        try:
            candidate = response.candidates[0]
            grounding_metadata = candidate.grounding_metadata
            lines = []

            text_content = ""
            for part in candidate.content.parts:
                if hasattr(part, 'text') and part.text and not bool(getattr(part, "thought", False)):
                    text_content += part.text

            if text_content:
                lines.append(text_content)

            lines.append("\n\n----\n## Grounding Sources\n")

            if grounding_metadata and hasattr(grounding_metadata, 'grounding_supports') and grounding_metadata.grounding_supports:
                ENCODING = "utf-8"
                text_bytes = text_content.encode(ENCODING) if text_content else b""
                last_byte_index = 0

                for support in grounding_metadata.grounding_supports:
                    if text_bytes:
                        lines.append(
                            text_bytes[last_byte_index : support.segment.end_index].decode(ENCODING)
                        )
                        footnotes = "".join([f"[{i + 1}]" for i in support.grounding_chunk_indices])
                        lines.append(f" {footnotes}")
                        last_byte_index = support.segment.end_index

                    if text_bytes and last_byte_index < len(text_bytes):
                        lines.append(text_bytes[last_byte_index:].decode(ENCODING))

            if grounding_metadata and hasattr(grounding_metadata, 'grounding_chunks') and grounding_metadata.grounding_chunks:
                lines.append("\n### Grounding Chunks\n")
                for i, chunk in enumerate(grounding_metadata.grounding_chunks, start=1):
                    context = chunk.web or chunk.retrieved_context or chunk.maps
                    if not context:
                        continue

                    uri = context.uri
                    title = context.title or "Source"

                    if uri:
                        uri = uri.replace(" ", "%20")
                        if uri.startswith("gs://"):
                            uri = uri.replace("gs://", "https://storage.googleapis.com/", 1)

                    lines.append(f"{i}. [{title}]({uri})\n")
                    if hasattr(context, "place_id") and context.place_id:
                        lines.append(f"    - Place ID: `{context.place_id}`\n\n")
                    if hasattr(context, "text") and context.text:
                        lines.append(f"{context.text}\n\n")

            if grounding_metadata and hasattr(grounding_metadata, 'web_search_queries') and grounding_metadata.web_search_queries:
                lines.append(f"\n**Web Search Queries:** {grounding_metadata.web_search_queries}\n")
                if hasattr(grounding_metadata, 'search_entry_point') and grounding_metadata.search_entry_point:
                    lines.append(f"\n**Search Entry Point:**\n{grounding_metadata.search_entry_point.rendered_content}\n")
            elif grounding_metadata and hasattr(grounding_metadata, 'retrieval_queries') and grounding_metadata.retrieval_queries:
                lines.append(f"\n**Retrieval Queries:** {grounding_metadata.retrieval_queries}\n")

            return "".join(lines)

        except Exception as e:
            candidate = response.candidates[0]
            text_content = ""
            for part in candidate.content.parts:
                if hasattr(part, 'text') and part.text and not bool(getattr(part, "thought", False)):
                    text_content += part.text
            return text_content + f"\n\nGrounding information not available: {str(e)}"
