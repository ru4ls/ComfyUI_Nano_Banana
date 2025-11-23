# ComfyUI_Nano_Banana

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Built with Gemini](https://img.shields.io/badge/Built_with-Gemini-blue.svg)](https://deepmind.google/technologies/gemini/)

A set of custom nodes for ComfyUI that leverage both Google Vertex AI and Google Generative AI SDK to generate images from text prompts, single images, and multiple images with configurable aspect ratios and resolutions using the Gemini Image model.

For a complete history of changes, see the [CHANGELOG.md](CHANGELOG.md) file.

## What's New

### Version 4.0 - The Grounding, Dual Approach & Project Structure Update
This major update adds powerful grounding with Google Search functionality, support for both Google Vertex AI and Google Generative AI API approaches, automatic project reorganization, and enhanced thinking process visibility.

#### New Feature:

**Grounding with Search Results!**
You can now generate images that are grounded in real-time Google Search results, with proper citations and source references. The new "Nano Banana Grounding with Search" node enables fact-based image generation with verifiable sources.

**Enhanced Output Information**
The grounding node provides three outputs: generated image, text response, and grounding sources with citations, allowing full transparency into the information sources used.

**Toggle Search Functionality**
The grounding node includes a boolean switch to enable or disable the Google Search tool as needed.

**Dual Authentication Approach Support!**
You can now use either Google Vertex AI approach (with PROJECT_ID and LOCATION) or Google Generative AI API approach (with GOOGLE_API_KEY) - the system automatically detects and uses the available credentials.

**Thinking Process Output**
The base Nano Banana node now outputs the AI's thought process when using Vertex AI, providing insights into the AI's reasoning and decision-making.

**Project Structure Reorganization**
The codebase has been reorganized into dedicated `core/`, `nodes/`, and `utils/` directories for better maintainability and following Python best practices.

**Automatic Location Override**
Models like gemini-3-pro-image-preview automatically use the global endpoint regardless of your LOCATION setting, ensuring compatibility across different user configurations.

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

### Option 1: Google Generative AI API (Recommended for beginners)
To use the simpler API approach, you need a Google AI API key. You can obtain one from the [Google AI Studio](https://aistudio.google.com/app/apikey). Please note that the Gemini API is a paid service and may incur costs.

1. Copy the `.env.api.template` file to create your `.env` file:
   ```bash
   cp .env.api.template .env
   ```
2. Edit the `.env` file and replace `YOUR_API_KEY` with your actual API key:
   ```
   GOOGLE_API_KEY="your-actual-api-key-here"
   ```

### Option 2: Google Vertex AI (For advanced users with full functionality)
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
*   `thinking` (STRING): The AI's thought process and reasoning (only available when using Vertex AI approach; shows helpful message for API users).

### Nano Banana Grounding

This node enables image generation that is grounded in real-time Google Search results, with proper citations and source references. It allows for fact-based image generation with verifiable information from the web. The node provides transparency into the information sources used to generate the content.

**Inputs:**

*   `model_name` (STRING): The Gemini model to use. Currently using: `gemini-3-pro-image-preview` for advanced capabilities (default: `gemini-3-pro-image-preview`).
*   `prompt` (STRING): The text prompt for image generation that will be used to search and generate images based on search results.
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

*   `image` (IMAGE): The generated image based on search results.
*   `text_response` (STRING): The AI's response text (only available when using Vertex AI approach; shows helpful message for API users).
*   `grounding_sources` (STRING): Citation information with source URLs and search queries used to generate the response.

**Note:** When using the Google Generative AI API approach (as opposed to VertexAI), the text_response and grounding_sources will include helpful messages about using Vertex AI for full capabilities.

## Example Usage

### Text to Image Generation (with configurable aspect ratio)

1.  Add the `NanoBanana` node to your workflow.
2.  Select your desired `aspect_ratio` from the dropdown (e.g., `16:9` for wide landscape, `9:16` for vertical, etc.).
3.  Enter a `prompt`.
4.  Ensure no `image_` inputs are connected.
5.  Connect the output `image` to a `PreviewImage` or `SaveImage` node to see the result.

**Sample Prompt:** "A cinematic close-up of a transparent glass chess piece (a knight) aimed at the camera. Inside the glass piece, a tiny glowing galaxy swirls with purple and gold nebulae. The background is a dimly lit library with dust motes dancing in a single shaft of volumetric golden hour light striking the chess piece, creating caustic light refractions on the wooden table."


### Image Editing and Image Fusion Generation (with configurable aspect ratio and 1 to 6 reference images)

1.  Add the `NanoBanana` node to your workflow.
2.  Select your desired `aspect_ratio` from the dropdown (the original images will be adapted to this output aspect ratio).
3.  Connect one or more `LoadImage` nodes (up to 6) to the `image_1` to `image_6` inputs.
4.  Enter a `prompt` describing the desired changes or outcome.
5.  Connect the output `image` to a `PreviewImage` or `SaveImage` node to see the result.

**Sample Prompt:** "A high-speed freeze-frame photograph of the glass chess knight shattering into thousands of sharp, crystalline shards. The galaxy inside is bursting outward, spilling purple and gold nebulae mist into the room. The glass fragments are suspended in mid-air, each one refracting the golden sunlight and the internal galaxy light. The wooden table is covered in glittering debris. Maintain the realistic depth of field and volumetric dust."


### Grounding with Search Results Generation

1.  Add the `NanoBananaGrounding` node to your workflow.
2.  Enter a `prompt` that requires current data or information from the web (e.g., weather forecasts, current events, trending topics).
3.  Toggle the `use_search` parameter to `True` to enable Google Search functionality.
4.  Optionally connect reference images if needed.
5.  Set the desired `aspect_ratio` and `image_size` based on your needs.
6.  Connect the two outputs: `image` and `grounding_sources` to appropriate display nodes.
7.  The `grounding_sources` output will contain citations and links to the sources used in generating the response.

**Sample Prompt:** "Search for and visualize the current weather forecast for the next 5 days in San Francisco in a clean, modern glass hud style with the city as a bacground weather chart. Add a realistic visual of what I could wear each day."

**Example Workflow:**
- The node will perform a Google search based on your prompt
- Generate an image based on the search results
- List all sources and citations used in the generation process


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
