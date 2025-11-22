# ComfyUI_Nano_Banana

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Built with Gemini](https://img.shields.io/badge/Built_with-Gemini-blue.svg)](https://deepmind.google/technologies/gemini/)

A set of custom nodes for ComfyUI that leverage the official Google Generative AI SDK to generate images from text prompts, single images, and multiple images with configurable aspect ratios and resolutions using the Gemini Image model.

## Whats New
### Version 3.0 - The Pro & Stability Update
This update brings advanced capabilities from the Gemini Pro models including image size selection, focused on the most stable Pro model for enhanced image generation.

New Feature: Image Quality Control!
You can now select from different image quality/size options (1K, 2K, 4K) for better control over output quality and generation speed.

New Feature: Enhanced Multi-Image Support
Now supports up to 6 reference images for advanced image fusion and editing, based on the latest Gemini Pro capabilities.

New Feature: Pro Model Focus
Now optimized for gemini-3-pro-image-preview for the most advanced image generation capabilities.

Improved: Error Handling
Better validation and error handling with finish reason checking for more robust operation.

### Version 2.0 - The Fusion & Control Update
This was a complete overhaul of the Nano Banana node, moving from a gemini-2.5-flash-image-preview model to gemini-2.5-flash-image.

Feature: Full Aspect Ratio Control!
The single biggest upgrade. You can now select from 10 different aspect ratios (like 16:9, 9:16, 4:3, etc.) and the node will generate an image with the correct dimensions. The old 1024x1024 limitation has been removed.

Feature: Creative Control with Temperature
A new temperature input was added, allowing you to control the randomness and creativity of the generated image.

Improved: Multi-Image Fusion
Image-to-image workflows were rebuilt from the ground up. The node now robustly supports true multi-image fusion using up to three reference images.

Removed:
The non-functional width, height, and seed inputs were removed in favor of the superior aspect_ratio and temperature controls.

## Installation

1.  Clone this repository into your `custom_nodes` folder.
    ```bash
    cd ComfyUI/custom_nodes
    git clone https://github.com/ru4ls/ComfyUI_Nano_Banana.git
    ```
2.  Install the required dependencies:
    ```bash
    pip install -r ComfyUI_Nano_Banana/requirements.txt
    ```

## API Key Setup

To use these nodes, you need a Google AI API key. You can obtain one from the [Google AI Studio](https://aistudio.google.com/app/apikey). Please note that the Gemini API is a paid service and may incur costs.

Create a `.env` file in the `ComfyUI_Nano_Banana` directory with the following content:

```
GOOGLE_API_KEY="YOUR_API_KEY"
```

## Nodes

### Nano Banana

This node provides a flexible interface for image generation with support for multiple aspect ratios and image sizes, supporting text-to-image and image-to-image workflows with up to three reference images using the official Google Generative AI SDK. New features include model thought process visibility.

**Inputs:**

*   `model_name` (STRING): The Gemini model to use. Currently using: `gemini-3-pro-image-preview` for advanced capabilities (default: `gemini-3-pro-image-preview`).
*   `prompt` (STRING): The text prompt for image generation or manipulation.
*   `image_1` to `image_6` (IMAGE, optional): Up to six reference images. Provide at least one image for image-to-image generation.
*   `aspect_ratio` (STRING): The output aspect ratio for the generated image. Options include: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` (default: `1:1`).
*   `image_size` (STRING): The output image quality/size. Options include: `1K`, `2K`, `4K` (default: `2K`).
*   `temperature` (FLOAT, optional): Controls the creative randomness of the output. Higher values (e.g., 1.2) are more creative, lower values (e.g., 0.5) are more deterministic.


**Available Aspect Ratios & Resolutions:**
*   `1:1` - 1024x1024 (square)
*   `2:3` - 832x1248 (portrait)
*   `3:2` - 1248x832 (landscape)
*   `3:4` - 864x1184 (portrait)
*   `4:3` - 1184x864 (landscape)
*   `4:5` - 896x1152 (portrait)
*   `5:4` - 1152x896 (landscape)
*   `9:16` - 768x1344 (vertical/video)
*   `16:9` - 1344x768 (horizontal/video)
*   `21:9` - 1536x672 (ultrawide)

**Outputs:**

*   `image` (IMAGE): The generated image.

## Example Usage

!Important Make sure your API key is set up in the `.env` file.

### Text to Image Generation (with configurable aspect ratio)

1.  Add the `NanoBanana` node to your workflow.
2.  Select your desired `aspect_ratio` from the dropdown (e.g., `16:9` for wide landscape, `9:16` for vertical, etc.).
3.  Enter a `prompt`.
4.  Ensure no `image_` inputs are connected.
5.  Connect the output `image` to a `PreviewImage` or `SaveImage` node to see the result.

**Sample Prompt:** "A cinematic close-up of a transparent glass chess piece (a knight) aimed at the camera. Inside the glass piece, a tiny glowing galaxy swirls with purple and gold nebulae. The background is a dimly lit library with dust motes dancing in a single shaft of volumetric golden hour light striking the chess piece, creating caustic light refractions on the wooden table."

<img width="1534" height="635" alt="Screenshot 2025-11-22 073404" src="https://github.com/user-attachments/assets/10c41dc3-074c-4112-afe9-30bc6a0091f0" />

<img width="1920" height="815" alt="NanoBanana_Pro_00004_" src="https://github.com/user-attachments/assets/73e67243-d412-41fb-82ee-841840db22c7" />


### Image Editing and Image Fusion Generation (with configurable aspect ratio and 1 to 6 reference images)

1.  Add the `NanoBanana` node to your workflow.
2.  Select your desired `aspect_ratio` from the dropdown (the original images will be adapted to this output aspect ratio).
3.  Connect one or more `LoadImage` nodes (up to 6) to the `image_1` to `image_6` inputs.
4.  Enter a `prompt` describing the desired changes or outcome.
5.  Connect the output `image` to a `PreviewImage` or `SaveImage` node to see the result.

**Sample Prompt:** "A high-speed freeze-frame photograph of the glass chess knight shattering into thousands of sharp, crystalline shards. The galaxy inside is bursting outward, spilling purple and gold nebulae mist into the room. The glass fragments are suspended in mid-air, each one refracting the golden sunlight and the internal galaxy light. The wooden table is covered in glittering debris. Maintain the realistic depth of field and volumetric dust."

<img width="1649" height="548" alt="Screenshot 2025-11-22 074627" src="https://github.com/user-attachments/assets/27477ae8-6a59-42a4-9d7d-ff6bb79eb048" />

<img width="1920" height="815" alt="NanoBanana_Pro_00005_" src="https://github.com/user-attachments/assets/1132c06a-5b9c-40bf-8358-2c9cef05210b" />


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
