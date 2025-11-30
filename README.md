# ComfyUI_Nano_Banana

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Built with Gemini](https://img.shields.io/badge/Built_with-Gemini-blue.svg)](https://deepmind.google/technologies/gemini/)

A set of custom nodes for ComfyUI that leverage both Google Vertex AI and Google Generative AI SDK to generate images from text prompts, single images, and multiple images with configurable aspect ratios and resolutions using the Gemini Image model.

## What's New

### Version 6.0 - The Multi-Turn Chat, Deprecation & Interactive Image Generation Update
This major update introduces a Multi-Turn Chat node that enables conversational image generation and editing with preserved context across multiple interactions, and deprecates legacy nodes in favor of a cleaner architecture.

#### New Features:

**Multi-Turn Chat Node!**
A new "Nano Banana Multi-Turn Chat" node that supports conversational image generation and editing. Maintains conversation history and allows iterative image modifications by referencing previous images as context for new generations. Includes reset functionality to start fresh conversations.

**Enhanced Conversation Context**
The node preserves conversation flow across multiple node executions, allowing for iterative improvements and refinements to generated images. Accepts initial images to start conversations and builds upon them in subsequent turns.

#### Changes:

**Deprecation of Legacy Nodes**
The NanoBanana and NanoBananaGrounding nodes are now deprecated in favor of the unified NanoBananaAIO node. All functionality from these nodes has been incorporated into the AIO node, resulting in a cleaner architecture with reduced code duplication and improved maintainability.

---

### Version 5.0 - The Unified AIO & Multi Image Generation Update
This major update introduces a unified All-in-One (AIO) node that combines all features from existing nodes into a single, powerful interface with support for both single and multiple image generation.

#### Previous Features:

**All-in-One (AIO) Node!**
A new unified "Nano Banana All-in-One" node that combines all features from existing nodes into a single interface. The node dynamically adapts its behavior based on the `image_count` parameter - generating a single image (like NanoBananaGrounding) or multiple images (like the deprecated NanoBananaInterleaved) with the same powerful grounding, search, and thinking capabilities.

**Multi Image Generation**
Generate up to 10 alternative images (1-10) with grounding and search capabilities in a single node execution. Images are generated with numbered prompts (e.g., "Image 1 of 3", "Image 2 of 3") to create variations. All generated images, text responses, and grounding sources are combined into the appropriate outputs.

**Backward Compatibility**
Existing nodes (NanoBanana, NanoBananaGrounding) are maintained for compatibility with existing workflows.

**Cleaner Architecture**
Reduced code redundancy with shared functionality between single and multiple image generation modes, making the codebase more maintainable and efficient.

---

For a complete history of changes, see the [CHANGELOG.md](CHANGELOG.md) file.

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

## Configuration Setup

You can use either Google Generative AI API approach (simpler) or Google Vertex AI approach (more powerful) depending on your needs.

### Option 1: Google Generative AI API
To use the simpler API approach, you need a Google AI API key. You can obtain one from the [Google AI Studio](https://aistudio.google.com/app/apikey). Please note that the Gemini API is a paid service and may incur costs.

1. Copy the `.env.api.template` file to create your `.env` file:
   ```bash
   cp .env.api.template .env
   ```
2. Edit the `.env` file and replace `YOUR_API_KEY` with your actual API key:
   ```
   GOOGLE_API_KEY="your-actual-api-key-here"
   ```

### Option 2: Google Vertex AI
For access to the full functionality including the thinking process output and enhanced grounding capabilities, use the Vertex AI approach with your Google Cloud Project.

To use this you need a Google Cloud Project with the Vertex AI API enabled.

1.  **Enable the Vertex AI API:** Follow the instructions in the [Google Cloud documentation](https://cloud.google.com/vertex-ai/docs/start/cloud-environment) to enable the API for your project.

2.  **Authenticate Your Environment:** This node uses Application Default Credentials (ADC) to securely authenticate with Google Cloud. Run the following `gcloud` command in your terminal to log in and set up your credentials. This is a one-time setup.
    ```bash
    gcloud auth application-default login
    ```
    The node authenticates directly through the installed Python libraries and does **not** depend on the `gcloud.cmd` executable being available in your system's PATH at runtime.

3.  **Create a `.env` file:** Copy the `.env.vertexai.template` file to create your `.env` file:
    ```bash
    cp .env.vertexai.template .env
    ```
    Then edit the `.env` file and add your Google Cloud project details:
    ```
    PROJECT_ID="your-gcp-project-id"
    LOCATION="your-gcp-location"  # e.g., us-central1 (Note: gemini-3-pro models automatically use global endpoint)
    ```

### Automatic Approach Detection
The system automatically detects and uses the available credentials:
- If both PROJECT_ID and LOCATION are set, it uses the Vertex AI approach
- If only GOOGLE_API_KEY is set, it uses the API approach
- If neither is available, an error is shown

## Nodes

### Nano Banana (DEPRECATED)

This node is now deprecated. Please use the "Nano Banana All-in-One" node instead, which includes all the functionality of this node plus additional features like multiple image generation and grounding capabilities.

This node previously provided a flexible interface for image generation with support for multiple aspect ratios and image sizes, supporting text-to-image and image-to-image workflows with up to three reference images using the official Google Generative AI SDK. New features included model thought process visibility.

### Nano Banana Grounding (DEPRECATED)

This node is now deprecated. Please use the "Nano Banana All-in-One" node instead, which includes all the functionality of this node plus additional features like multiple image generation and improved capabilities.

This node previously enabled image generation that was grounded in real-time Google Search results, with proper citations and source references. It allowed for fact-based image generation with verifiable information from the web.

### Nano Banana All-in-One (AIO)

This unified node combines all features from the existing nodes into a single, powerful interface. It dynamically adapts its behavior based on the `image_count` parameter: generating a single image (like NanoBananaGrounding) or multiple images (1-10) with the same powerful grounding, search, and thinking capabilities. This is the recommended node for new workflows.

**Inputs:**

*   `model_name` (STRING): The Gemini model to use. Currently using: `gemini-3-pro-image-preview` for advanced capabilities (default: `gemini-3-pro-image-preview`).
*   `prompt` (STRING): The text prompt for image generation or manipulation.
*   `image_count` (INT): Number of images to generate (1-10). When set to 1, behaves like NanoBananaGrounding; when >1, generates multiple sequential images (default: 1).
*   `use_search` (BOOLEAN): Toggle to enable or disable Google Search functionality (default: `True`).
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

*   `images` (IMAGE): Batch of generated images (single image when image_count=1, multiple images when image_count>1).
*   `thinking` (STRING): The AI's thought process and reasoning (only available when using Vertex AI approach; shows helpful message for API users).
*   `grounding_sources` (STRING): Citation information with source URLs and search queries used to generate the response.

**Note:** When using the Google Generative AI API approach (as opposed to VertexAI), the thinking and grounding_sources outputs will include helpful messages about using Vertex AI for full capabilities.

### Nano Banana Multi-Turn Chat

This node supports conversational image generation and editing with preserved context across multiple interactions. Maintains conversation history and allows iterative image modifications by referencing previous images as context for new generations. Includes reset functionality to start fresh conversations.

**Inputs:**

*   `model_name` (STRING): The Gemini model to use. Currently using: `gemini-3-pro-image-preview` for advanced capabilities (default: `gemini-3-pro-image-preview`).
*   `prompt` (STRING): The text prompt for image generation or modification based on previous conversation context.
*   `reset_chat` (BOOLEAN): Toggle to reset the conversation history and start a fresh chat session (default: `False`).
*   `aspect_ratio` (STRING): The output aspect ratio for the generated image. Options include: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` (default: `1:1`).
*   `image_size` (STRING): The output image quality/size. Options include: `1K`, `2K`, `4K` (default: `2K`).
*   `temperature` (FLOAT): Controls the creative randomness of the output. Higher values (e.g., 1.2) are more creative, lower values (e.g., 0.5) are more deterministic (default: 1.0).
*   `image_input` (IMAGE, optional): Initial image to start the conversation with. Use this to provide an initial image for the first interaction in a conversation.

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

*   `image` (IMAGE): The generated image based on the current prompt and conversation context.
*   `response_text` (STRING): The AI's response text to the current prompt.
*   `metadata` (STRING): Generation metadata including finish reason and safety ratings.
*   `chat_history` (STRING): Complete conversation history with all prompts and responses.

## Example Usage

### Text to Image Generation (with configurable aspect ratio)

1.  Add the `NanoBanana` node to your workflow.
2.  Select your desired `aspect_ratio` from the dropdown (e.g., `16:9` for wide landscape, `9:16` for vertical, etc.).
3.  Enter a `prompt`.
4.  Ensure no `image_` inputs are connected.
5.  Connect the output `image` to a `PreviewImage` or `SaveImage` node to see the result.

**Sample Prompt:** "A cinematic close-up of a transparent glass chess piece (a knight) aimed at the camera. Inside the glass piece, a tiny glowing galaxy swirls with purple and gold nebulae. The background is a dimly lit library with dust motes dancing in a single shaft of volumetric golden hour light striking the chess piece, creating caustic light refractions on the wooden table."

<img width="1540" height="495" alt="Screenshot 2025-11-23 113738" src="https://github.com/user-attachments/assets/9ded57b5-b0a8-4de8-b201-93f429fc050f" />
<img width="1920" height="815" alt="NanoBanana_Pro_00010_" src="https://github.com/user-attachments/assets/020f7a72-d2d7-4c06-948c-3e1afa2887dc" />


### Image Editing and Image Fusion Generation (with configurable aspect ratio and 1 to 6 reference images)

1.  Add the `NanoBanana` node to your workflow.
2.  Select your desired `aspect_ratio` from the dropdown (the original images will be adapted to this output aspect ratio).
3.  Connect one or more `LoadImage` nodes (up to 6) to the `image_1` to `image_6` inputs.
4.  Enter a `prompt` describing the desired changes or outcome.
5.  Connect the output `image` to a `PreviewImage` or `SaveImage` node to see the result.

**Sample Prompt:** "A high-speed freeze-frame photograph of the glass chess knight shattering into thousands of sharp, crystalline shards. The galaxy inside is bursting outward, spilling purple and gold nebulae mist into the room. The glass fragments are suspended in mid-air, each one refracting the golden sunlight and the internal galaxy light. The wooden table is covered in glittering debris. Maintain the realistic depth of field and volumetric dust."

<img width="1717" height="473" alt="Screenshot 2025-11-23 114319" src="https://github.com/user-attachments/assets/1d161151-d7ab-43f1-b683-fb8838d00430" />
<img width="1920" height="815" alt="NanoBanana_Pro_00011_" src="https://github.com/user-attachments/assets/eaf03061-f419-4782-b9a1-864b8b52103b" />


### Grounding with Search Results Generation

1.  Add the `NanoBananaGrounding` node to your workflow.
2.  Enter a `prompt` that requires current data or information from the web (e.g., weather forecasts, current events, trending topics).
3.  Toggle the `use_search` parameter to `True` to enable Google Search functionality.
4.  Optionally connect reference images if needed.
5.  Set the desired `aspect_ratio` and `image_size` based on your needs.
6.  Connect the two outputs: `image` and `grounding_sources` to appropriate display nodes.
7.  The `grounding_sources` output will contain citations and links to the sources used in generating the response.

**Sample Prompt:** "Search for and visualize the current weather forecast for the next 5 days in Jakarta in a clean, modern glass hud style with the city as a background weather chart. Add a realistic visual of what I could wear each day."

**Example Workflow:**
- The node will perform a Google search based on your prompt
- Generate an image based on the search results
- List all sources and citations used in the generation process

<img width="1809" height="494" alt="Screenshot 2025-11-23 115440" src="https://github.com/user-attachments/assets/a5642e7c-d801-4a87-ba85-f7d2f4221541" />
<img width="1920" height="814" alt="NanoBanana_Pro_00012_" src="https://github.com/user-attachments/assets/da5af049-01a3-49b2-88ba-26d8b92050e4" />

**Sample Prompt:** "Using provided image ensure style consistency, composition and how data displayed. Search for and visualize the current weather forecast for the next 5 days in [CITY], with the city iconic spot as a background weather chart.

CITY
image 1 of 4 Jakarta.
image 2 of 4 Tokyo.
image 3 of 4 London.
image 4 of 4 Amsterdam."

**Example Workflow:**
- The node will perform a Google search based on your prompt
- Generate a set of images with image reference style based on the search results
- List all sources and citations used in the generation process


### Multi-Turn Chat Conversation (with preserved context)

1.  Add the `NanoBananaMultiTurnChat` node to your workflow.
2.  Enter your initial `prompt` to generate the first image.
3.  Optionally connect an initial `image_input` to start the conversation with a specific image.
4.  Set your desired `aspect_ratio` and `image_size` parameters.
5.  Execute the node to generate the initial image and response.
6.  For subsequent interactions, use the same node instance with the same parameters but change the `prompt` to continue the conversation and modify the image iteratively.
7.  Use `reset_chat` to start a fresh conversation when needed.
8.  Connect the output `image` to a `PreviewImage` or `SaveImage` node to see the results.
9.  The `chat_history` output shows the complete conversation history.

**Example Workflow:**
- First execution: "Create an image of a clear perfume bottle sitting on a vanity"
- Second execution: "Change the color of the liquid inside the glass bottle to a vibrant royal blue"
- Third execution: "Extreme close-up on the glass texture and silver cap of the blue perfume bottle. The framing is cropped tightly and weighted to the left"


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
