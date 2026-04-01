import os
from pathlib import Path

DEFAULT_BASE_MODEL = "runwayml/stable-diffusion-v1-5"
DEFAULT_LORA_PATH = "gs://minetexture-checkpoints/Minecraft-Textures.safetensors"
DEFAULT_OUTPUT_DIR = Path("data/output")

DEFAULT_STEPS = 30
DEFAULT_GUIDANCE_SCALE = 7.5
DEFAULT_HEIGHT = 512
DEFAULT_WIDTH = 512
DEFAULT_NEGATIVE_PROMPT = ""
DEFAULT_USE_LCM = False

BASE_MODEL = os.getenv("BASE_MODEL", DEFAULT_BASE_MODEL)
LORA_PATH = os.getenv("LORA_PATH", DEFAULT_LORA_PATH)
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR)))
INFERENCE_BUCKET = os.getenv("INFERENCE_BUCKET", "generated_data_minetexture")

STEPS = int(os.getenv("STEPS", str(DEFAULT_STEPS)))
GUIDANCE_SCALE = float(os.getenv("GUIDANCE_SCALE", str(DEFAULT_GUIDANCE_SCALE)))
HEIGHT = int(os.getenv("HEIGHT", str(DEFAULT_HEIGHT)))
WIDTH = int(os.getenv("WIDTH", str(DEFAULT_WIDTH)))
NEGATIVE_PROMPT = os.getenv("NEGATIVE_PROMPT", DEFAULT_NEGATIVE_PROMPT)
USE_LCM = os.getenv("USE_LCM", str(DEFAULT_USE_LCM)).lower() in ("true", "1", "yes")
