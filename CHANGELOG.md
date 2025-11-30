# Changelog

All notable changes to the ComfyUI_Nano_Banana project will be documented in this file.

## [6.0.0] - The Multi-Turn Chat, Deprecation & Interactive Image Generation Update 2025-11-30
### Added
- Multi-Turn Chat Node
  - New "Nano Banana Multi-Turn Chat" node that supports conversational image generation and editing
  - Maintains conversation history and allows iterative image modifications
  - Accepts initial images to start conversations and builds upon them in subsequent turns
  - Returns generated image, text response, metadata, and conversation history
  - Includes reset_chat functionality to start fresh conversations
- Enhanced Conversation Context
  - Ability to reference previous images as context for new generations
  - Preserves conversation flow across multiple node executions
  - Improved error handling for client connection issues
### Changed
- Deprecation of Legacy Nodes
  - NanoBanana and NanoBananaGrounding nodes are now deprecated in favor of the unified NanoBananaAIO
  - Updated documentation to reflect the deprecation status
  - All functionality from the deprecated nodes is available in the AIO node
- Node Architecture Improvement
  - Cleaner codebase with removal of redundant legacy nodes
  - Reduced code duplication and improved maintainability

## [5.0.0] - The Unified AIO & Multi Image Generation Update 2025-11-24
### Added
- All-In-One (AIO) Node
  - New "Nano Banana All-in-One" node that combines all features from existing nodes
  - Single node handles both single and multiple image generation (1-10 images)
  - Includes grounding, search, thinking, aspect ratio, image size, and temperature controls
  - Dynamic behavior based on image_count parameter: single image or multiple images
- Multi Image Generation
  - Support for generating up to 10 alternative images with grounding and search capabilities
  - Images generated with numbered prompts (e.g., "Image 1 of 3", "Image 2 of 3") to create variations
  - Combined outputs for multiple images, text responses, and grounding sources
- Backward Compatibility Maintenance
  - Retained existing nodes (NanoBanana, NanoBananaGrounding) for compatibility
- Enhanced Node Architecture
  - Cleaner, more maintainable code structure with shared functionality
  - Reduced redundancy across node implementations

## [4.0.0] - The Grounding, Dual Approach & Project Structure Update 2025-11-23
### Added
- Grounding with Search Results functionality
  - New "Nano Banana Grounding" node that generates images based on Google Search results
  - Real-time search integration with proper citations and source references
  - Three outputs: generated image, text response, and grounding sources
  - Toggle to enable/disable search functionality
- Enhanced output information with transparency into information sources
- Dual Authentication Approach Support
  - Support for both Google Vertex AI (with PROJECT_ID and LOCATION) and Google Generative AI API (with GOOGLE_API_KEY) approaches
  - Automatic detection and switching between approaches based on available credentials
  - Enhanced functionality when using Vertex AI (access to full text response and thinking process)
  - Helpful guidance messages when API approach is used
- Thinking Process Output
  - New "thinking" output in the base NanoBanana node when using Vertex AI
  - Provides insights into the AI's reasoning and decision-making process
- Project Structure Reorganization
  - Dedicated `core/`, `nodes/`, and `utils/` directories for better code organization
  - Proper module structure following Python/ComfyUI best practices
- Location Override Feature
  - Automatic use of global location for gemini-3-pro models to ensure compatibility
  - Models like gemini-3-pro-image-preview always use global endpoint regardless of user's LOCATION setting
  - Fixes compatibility issues with different user LOCATION configurations

## [3.0.0] - The Pro & Stability Update 2025-11-22
### Added
- Image Quality Control with options for 1K, 2K, 4K image sizes
- Enhanced Multi-Image Support supporting up to 6 reference images
- Pro Model Focus optimized for gemini-3-pro-image-preview
- Better error handling with finish reason checking

## [2.0.0] - The Fusion & Control Update 2025-10-10
### Added
- Full Aspect Ratio Control with 10 different aspect ratios (1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9)
- Creative Control with Temperature parameter for randomness
- Robust multi-image fusion supporting up to three reference images

### Removed
- Non-functional width, height, and seed inputs
- Old 1024x1024 limitation

## [1.0.0] - Initial Release 2025-09-07
### Added
- Basic Nano Banana node for text-to-image generation
- Support for image-to-image workflows
- Initial Google Generative AI SDK integration
