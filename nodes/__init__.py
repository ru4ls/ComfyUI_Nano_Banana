from .nano_banana_aio import NanoBananaAIO
from .nano_banana_multiturn_chat import NanoBananaMultiTurnChat

NODE_CLASS_MAPPINGS = {
    "NanoBananaAIO": NanoBananaAIO,
    "NanoBananaMultiTurnChat": NanoBananaMultiTurnChat
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NanoBananaAIO": "Nano Banana AIO",
    "NanoBananaMultiTurnChat": "Nano Banana Multi-Turn Chat"
}