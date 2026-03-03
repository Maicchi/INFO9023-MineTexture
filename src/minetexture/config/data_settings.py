from pathlib import Path
from typing import Tuple, Set

# Directories
DEFAULT_RAW_DIR = Path("data/raw")
DEFAULT_PROCESSED_DIR = Path("data/processed")

# Image settings
TARGET_SIZE = 512
BG_COLOR: Tuple[int, int, int, int] = (0, 255, 0, 255)

# File extensions
ALLOWED_EXTENSIONS: Set[str] = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}

# Minecraft specific paths
MINECRAFT_TEXTURE_PATHS = [
    "assets/minecraft/textures/block",
    "assets/minecraft/textures/blocks",
    "assets/minecraft/textures/item",
    "assets/minecraft/textures/items",
    "assets/minecraft/textures/entity",
    "assets/minecraft/textures/entities",
    "assets/minecraft/textures/gui/hanging_signs",
    "assets/minecraft/textures/map",
    "pack.png",
]
