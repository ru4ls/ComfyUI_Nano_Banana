
from .nodes.nano_banana_nodes import NanoBanana
from .nodes.nano_banana_grounding_nodes import NanoBananaGrounding

NODE_CLASS_MAPPINGS = {
    "NanoBanana": NanoBanana,
    "NanoBananaGrounding": NanoBananaGrounding,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NanoBanana": "Nano Banana",
    "NanoBananaGrounding": "Nano Banana Grounding",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
