
from .nodes.nano_banana_nodes import NanoBanana
from .nodes.nano_banana_grounding_nodes import NanoBananaGrounding
from .nodes.nano_banana_aio import NanoBananaAIO

NODE_CLASS_MAPPINGS = {
    "NanoBanana": NanoBanana,
    "NanoBananaGrounding": NanoBananaGrounding,
    "NanoBananaAIO": NanoBananaAIO,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NanoBanana": "Nano Banana",
    "NanoBananaGrounding": "Nano Banana Grounding",
    "NanoBananaAIO": "Nano Banana All-in-One",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
