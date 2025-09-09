
from .nano_banana_nodes import NanoBananaTextToImage, NanoBananaImageToImage, NanoBananaMultiImageToImage

NODE_CLASS_MAPPINGS = {
    "NanoBananaTextToImage": NanoBananaTextToImage,
    "NanoBananaImageToImage": NanoBananaImageToImage,
    "NanoBananaMultiImageToImage": NanoBananaMultiImageToImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NanoBananaTextToImage": "Nano Banana Text to Image",
    "NanoBananaImageToImage": "Nano Banana Image to Image",
    "NanoBananaMultiImageToImage": "Nano Banana Multi-Image to Image",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
