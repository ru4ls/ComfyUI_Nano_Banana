import torch
import numpy as np
from PIL import Image

def tensor_to_pil(image_tensor):
    """Convert a PyTorch tensor to PIL Image"""
    if image_tensor is None:
        return None
    return Image.fromarray((image_tensor[0].cpu().numpy() * 255.).astype(np.uint8))

def pil_to_tensor(pil_image):
    """Convert a PIL Image to PyTorch tensor"""
    if pil_image is None:
        return None
    image_np = np.array(pil_image).astype(np.float32) / 255.0
    return torch.from_numpy(image_np)[None,]