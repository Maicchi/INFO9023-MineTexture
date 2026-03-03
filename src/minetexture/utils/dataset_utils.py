from __future__ import annotations

from pathlib import Path
from typing import List
from PIL import Image

from minetexture.config.data_settings import TARGET_SIZE, BG_COLOR, ALLOWED_EXTENSIONS

def is_allowed_image(p: Path) -> bool:
    """
    Check if a file is an allowed image type based on its extension.
    """
    return p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS


def list_images(path: Path) -> List[Path]:
    """
    List all allowed image files in a given path. 
    """
    if path.is_file():
        return [path] if is_allowed_image(path) else []

    if not path.is_dir():
        return []

    return sorted(p for p in path.rglob("*") if is_allowed_image(p))

def ensure_dir_exists(dir_path: Path) -> Path:
    """
    Check the existence of a directory and create it if it doesn't exist.
    """
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def load_image(path: Path) -> Image.Image:
    """
    Load an image from disk and convert it to RGBA mode.
    """
    return Image.open(path).convert("RGBA")


def handle_transparency(img: Image.Image, color=BG_COLOR) -> Image.Image:
    """
    Replace transparant pixels in an image with a solid background color.
    """
    bg = Image.new("RGBA", img.size, color)
    return Image.alpha_composite(bg, img)


def resize_image(img: Image.Image, target_size: int = TARGET_SIZE) -> Image.Image:
    """
    Resize image to a fixed target size
    """
    if img.size != (target_size, target_size):
        return img.resize((target_size, target_size), Image.NEAREST)
    return img


def process_image(path: Path) -> Image.Image:
    """
    Full image preprocessing pipeline
    """
    img = load_image(path)
    img = handle_transparency(img)
    img = resize_image(img)
    return img