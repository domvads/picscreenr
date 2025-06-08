"""Image captioning service using Hugging Face transformers."""

from typing import List
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from PIL import Image
import torch


def load_model(model_name: str = "nlpconnect/vit-gpt2-image-captioning"):
    model = VisionEncoderDecoderModel.from_pretrained(model_name)
    processor = ViTImageProcessor.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model, processor, tokenizer


def generate_caption(model, processor, tokenizer, image_path: str) -> str:
    """Generate a caption for the given image."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    image = Image.open(image_path).convert("RGB")
    pixel_values = processor(images=[image], return_tensors="pt").pixel_values.to(device)

    output_ids = model.generate(pixel_values, max_length=16, num_beams=4)
    caption = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return caption


def extract_tags(caption: str, max_tags: int = 5) -> List[str]:
    """Extract simple tags from caption by splitting words."""
    words = caption.lower().replace('.', '').split()
    unique_words = []
    for w in words:
        if w not in unique_words:
            unique_words.append(w)
    return unique_words[:max_tags]
