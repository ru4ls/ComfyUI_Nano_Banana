import io, torch, numpy as np
from PIL import Image

from google import genai
from google.genai import types

from ..core.auth import detect_approach, PROJECT_ID, LOCATION, GOOGLE_API_KEY
from ..utils.image_utils import tensor_to_pil

class NanoBananaAIO:
    """A unified multimodal node combining all features: single/multiple image generation, grounding, search, and thinking capabilities."""
    def __init__(self):
        self.client = None

    @classmethod
    def INPUT_TYPES(s):
        model_list = ["gemini-3-pro-image-preview"]
        return {
            "required": {
                "model_name": (model_list, {"default": model_list[0]}),
                "prompt": ("STRING", {"multiline": True, "default": "A futuristic nano banana dish"}),
                "image_count": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1}),
                "use_search": ("BOOLEAN", {"default": True})
            },
            "optional": {
                "image_1": ("IMAGE",), "image_2": ("IMAGE",), "image_3": ("IMAGE",),
                "image_4": ("IMAGE",), "image_5": ("IMAGE",), "image_6": ("IMAGE",),
                "aspect_ratio": (["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"], {"default": "1:1"}),
                "image_size": (["1K", "2K", "4K"], {"default": "2K"}),
                "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("images", "thinking", "grounding_sources")

    FUNCTION = "generate_unified"
    CATEGORY = "Ru4ls/NanoBanana"

    def _handle_error(self, message):
        print(f"\033[91mERROR: {message}\033[0m")
        # Always return the same number of outputs to maintain ComfyUI compatibility
        return (torch.zeros(1, 64, 64, 3), "", "")

    def generate_unified(self, model_name, prompt, image_count=1, use_search=True, image_1=None, image_2=None, image_3=None, image_4=None, image_5=None, image_6=None, aspect_ratio="1:1", image_size="2K", temperature=1.0):
        try:
            approach = detect_approach()

            if not prompt or prompt.strip() == "":
                return self._handle_error("Prompt cannot be empty")

            if not model_name:
                return self._handle_error("Model name is required")

            # Validate image_count
            if image_count < 1 or image_count > 10:
                return self._handle_error("Image count must be between 1 and 10")

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

            # If image_count is 1, behave like single image generation, otherwise generate multiple
            if image_count == 1:
                # Single image generation (like NanoBananaGrounding)
                return self._generate_single_image(
                    model_name, prompt, use_search, approach, contents,
                    aspect_ratio, image_size, temperature
                )
            else:
                # Multiple image generation (like Multi Image Generation)
                return self._generate_multiple_images(
                    model_name, prompt, image_count, use_search, approach, contents,
                    aspect_ratio, image_size, temperature
                )

        except ValueError as e:
            return self._handle_error(f"ValueError in NanoBananaAIO: {e}")
        except TypeError as e:
            return self._handle_error(f"TypeError in NanoBananaAIO: {e}")
        except Exception as e:
            return self._handle_error(f"{type(e).__name__} in NanoBananaAIO: {e}")

    def _generate_single_image(self, model_name, prompt, use_search, approach, contents, aspect_ratio, image_size, temperature):
        """Generate a single image with grounding capabilities."""
        if approach == "VERTEXAI":
            if not PROJECT_ID or not LOCATION:
                return self._handle_error("PROJECT_ID or LOCATION not configured in .env for Vertex AI approach")

            # Use global location for nanobanana models as they may only be available on global endpoint
            location = "global" if "gemini-3-pro" in model_name else LOCATION
            client = genai.Client(vertexai=True, project=PROJECT_ID, location=location)

            # Create the full configuration with tools if search is enabled - only for supported models
            if use_search and "gemini-3-pro" in model_name:
                config = types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                        image_size=image_size
                    ),
                    temperature=temperature
                )

                # Add search tool if use_search is True and model supports it
                google_search = types.Tool(google_search=types.GoogleSearch())
                config.tools = [google_search]
            else:
                # For models that don't support tools or when search is disabled
                config = types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                        image_size=image_size
                    ),
                    temperature=temperature
                )
        else:  # API approach
            if not GOOGLE_API_KEY:
                return self._handle_error("GOOGLE_API_KEY not configured in .env for API approach")

            client = genai.Client(api_key=GOOGLE_API_KEY)

            # Create the full configuration with tools if search is enabled
            config = types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=image_size
                ),
                temperature=temperature
            )

            # Add search tool if use_search is True
            tools = []
            if use_search:
                google_search = types.Tool(google_search=types.GoogleSearch())
                tools.append(google_search)

            if tools:
                config.tools = tools

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

        # Parse the response
        image_bytes = None
        text_response = ""

        for part in response.candidates[0].content.parts:
            if part.inline_data and image_bytes is None:
                image_bytes = part.inline_data.data
            elif part.text:
                text_response += part.text

        # Extract grounding information
        grounding_sources = self.extract_grounding_data(response)

        if image_bytes is None:
            return self._handle_error("No image data found in the API response.")

        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        image_np = np.array(pil_image).astype(np.float32) / 255.0
        image_tensor = torch.from_numpy(image_np)[None,]

        # For API approach, provide a helpful message about needing Vertex AI for full text response
        if approach == "API":
            text_response = "To access the full text response, please use Vertex AI approach with PROJECT_ID and LOCATION set up. Visit https://cloud.google.com/vertex-ai/docs/generative-ai/learn/quickstarts for setup instructions."
            grounding_sources = f"{grounding_sources}\n\nFor full grounding capabilities, please use Vertex AI approach with PROJECT_ID and LOCATION configured.\nVisit https://cloud.google.com/vertex-ai/docs/generative-ai/learn/quickstarts for setup instructions."

        return (image_tensor, text_response, grounding_sources)

    def _generate_multiple_images(self, model_name, prompt, image_count, use_search, approach, contents, aspect_ratio, image_size, temperature):
        """Generate multiple images with grounding capabilities."""
        generated_images = []
        all_text_responses = []
        all_grounding_sources = []

        for i in range(image_count):
            # Modify the prompt slightly for each image in the sequence
            current_prompt = f"{prompt} (Image {i+1} of {image_count})"

            # Create a copy of contents with the updated prompt for this iteration
            current_contents = [current_prompt] + contents[1:]  # Keep images, update prompt

            if approach == "VERTEXAI":
                if not PROJECT_ID or not LOCATION:
                    return self._handle_error("PROJECT_ID or LOCATION not configured in .env for Vertex AI approach")

                # Use global location for nanobanana models as they may only be available on global endpoint
                location = "global" if "gemini-3-pro" in model_name else LOCATION
                client = genai.Client(vertexai=True, project=PROJECT_ID, location=location)

                # Create the full configuration with tools if search is enabled - only for supported models
                if use_search and "gemini-3-pro" in model_name:
                    config = types.GenerateContentConfig(
                        response_modalities=["TEXT", "IMAGE"],
                        image_config=types.ImageConfig(
                            aspect_ratio=aspect_ratio,
                            image_size=image_size
                        ),
                        temperature=temperature
                    )

                    # Add search tool if use_search is True and model supports it
                    google_search = types.Tool(google_search=types.GoogleSearch())
                    config.tools = [google_search]
                else:
                    # For models that don't support tools or when search is disabled
                    config = types.GenerateContentConfig(
                        response_modalities=["TEXT", "IMAGE"],
                        image_config=types.ImageConfig(
                            aspect_ratio=aspect_ratio,
                            image_size=image_size
                        ),
                        temperature=temperature
                    )
            else:  # API approach
                if not GOOGLE_API_KEY:
                    return self._handle_error("GOOGLE_API_KEY not configured in .env for API approach")

                client = genai.Client(api_key=GOOGLE_API_KEY)

                # Create the full configuration with tools if search is enabled
                config = types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                        image_size=image_size
                    ),
                    temperature=temperature
                )

                # Add search tool if use_search is True
                tools = []
                if use_search:
                    google_search = types.Tool(google_search=types.GoogleSearch())
                    tools.append(google_search)

                if tools:
                    config.tools = tools

            response = client.models.generate_content(
                model=model_name,
                contents=current_contents,
                config=config
            )

            # Validate response and check finish reason
            if not response.candidates:
                return self._handle_error("API returned no candidates.")

            # Check if generation was successful
            if hasattr(response.candidates[0], 'finish_reason') and response.candidates[0].finish_reason != types.FinishReason.STOP:
                reason = response.candidates[0].finish_reason
                return self._handle_error(f"Generation failed with reason: {reason}")

            # Parse the response
            image_bytes = None
            text_response = ""

            for part in response.candidates[0].content.parts:
                if part.inline_data and image_bytes is None:
                    image_bytes = part.inline_data.data
                elif part.text:
                    text_response += part.text

            # Extract grounding information
            grounding_sources = self.extract_grounding_data(response)

            if image_bytes is None:
                return self._handle_error("No image data found in the API response.")

            pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            image_np = np.array(pil_image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_np)[None,]

            generated_images.append(image_tensor)
            all_text_responses.append(text_response)
            all_grounding_sources.append(grounding_sources)

        # Combine all generated images into a single tensor
        # This assumes all images have the same dimensions
        if len(generated_images) > 0:
            combined_images = torch.cat(generated_images, dim=0)
        else:
            return self._handle_error("No images were generated.")

        # Combine all text responses
        combined_text_responses = "\n\n".join(all_text_responses)

        # Combine all grounding sources
        combined_grounding_sources = "\n\n".join(all_grounding_sources)

        # For API approach, provide a helpful message about needing Vertex AI for full text response
        if approach == "API":
            combined_text_responses = "To access the full text responses, please use Vertex AI approach with PROJECT_ID and LOCATION set up. Visit https://cloud.google.com/vertex-ai/docs/generative-ai/learn/quickstarts for setup instructions."
            combined_grounding_sources = f"{combined_grounding_sources}\n\nFor full grounding capabilities, please use Vertex AI approach with PROJECT_ID and LOCATION configured.\nVisit https://cloud.google.com/vertex-ai/docs/generative-ai/learn/quickstarts for setup instructions."

        return (combined_images, combined_text_responses, combined_grounding_sources)

    def extract_grounding_data(self, response):
        """Extracts grounding sources from the response."""
        try:
            candidate = response.candidates[0]
            grounding_metadata = candidate.grounding_metadata
            lines = []

            # Extract text from the content parts of the candidate
            text_content = ""
            for part in candidate.content.parts:
                if hasattr(part, 'text') and part.text:
                    text_content += part.text

            # Add the actual response text content first, even if no grounding supports
            if text_content:
                lines.append(text_content)

            lines.append("\n\n----\n## Grounding Sources\n")

            if grounding_metadata and hasattr(grounding_metadata, 'grounding_supports') and grounding_metadata.grounding_supports:
                # Add citation information if available
                ENCODING = "utf-8"
                text_bytes = text_content.encode(ENCODING) if text_content else b""
                last_byte_index = 0

                for support in grounding_metadata.grounding_supports:
                    if text_bytes:  # Only process citations if we have text
                        lines.append(
                            text_bytes[last_byte_index : support.segment.end_index].decode(ENCODING)
                        )

                        # Generate and append citation footnotes (e.g., "[1][2]")
                        footnotes = "".join([f"[{i + 1}]" for i in support.grounding_chunk_indices])
                        lines.append(f" {footnotes}")

                        # Update index for the next segment
                        last_byte_index = support.segment.end_index

                    # Append any remaining text after the last citation
                    if text_bytes and last_byte_index < len(text_bytes):
                        lines.append(text_bytes[last_byte_index:].decode(ENCODING))

            if grounding_metadata and hasattr(grounding_metadata, 'grounding_chunks') and grounding_metadata.grounding_chunks:
                # Build Grounding Sources Section
                lines.append("\n### Grounding Chunks\n")
                for i, chunk in enumerate(grounding_metadata.grounding_chunks, start=1):
                    context = chunk.web or chunk.retrieved_context or chunk.maps
                    if not context:
                        continue

                    uri = context.uri
                    title = context.title or "Source"

                    # Convert GCS URIs to public HTTPS URLs
                    if uri:
                        uri = uri.replace(" ", "%20")
                        if uri.startswith("gs://"):
                            uri = uri.replace(
                                "gs://", "https://storage.googleapis.com/", 1
                            )

                    lines.append(f"{i}. [{title}]({uri})\n")
                    if hasattr(context, "place_id") and context.place_id:
                        lines.append(f"    - Place ID: `{context.place_id}`\n\n")
                    if hasattr(context, "text") and context.text:
                        lines.append(f"{context.text}\n\n")

            # Add Search/Retrieval Queries
            if grounding_metadata and hasattr(grounding_metadata, 'web_search_queries') and grounding_metadata.web_search_queries:
                lines.append(
                    f"\n**Web Search Queries:** {grounding_metadata.web_search_queries}\n"
                )
                if hasattr(grounding_metadata, 'search_entry_point') and grounding_metadata.search_entry_point:
                    lines.append(
                        f"\n**Search Entry Point:**\n{grounding_metadata.search_entry_point.rendered_content}\n"
                    )
            elif grounding_metadata and hasattr(grounding_metadata, 'retrieval_queries') and grounding_metadata.retrieval_queries:
                lines.append(
                    f"\n**Retrieval Queries:** {grounding_metadata.retrieval_queries}\n"
                )

            return "".join(lines)

        except Exception as e:
            # If there's an error extracting grounding info, return the text content at minimum
            candidate = response.candidates[0]
            text_content = ""
            for part in candidate.content.parts:
                if hasattr(part, 'text') and part.text:
                    text_content += part.text
            return text_content + f"\n\nGrounding information not available: {str(e)}"