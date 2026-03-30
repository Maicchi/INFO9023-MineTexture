from __future__ import annotations

import re
from datetime import datetime

from minetexture.config.inference_settings import (
    BASE_MODEL,
    GUIDANCE_SCALE,
    HEIGHT,
    INFERENCE_BUCKET,
    LORA_PATH,
    NEGATIVE_PROMPT,
    OUTPUT_DIR,
    STEPS,
    USE_LCM,
    WIDTH,
)
from minetexture.inference.generator import (
    build_pipeline,
    generate_image,
    resolve_lora_path,
)
from minetexture.utils.inference_utils import upload_image_to_gcs

_PIPELINES: dict[bool, object] = {}


def get_pipeline(use_lcm: bool = USE_LCM):
    if not LORA_PATH:
        raise ValueError("LORA_PATH is not set.")

    if use_lcm not in _PIPELINES:
        resolved_lora_path = resolve_lora_path(LORA_PATH)
        _PIPELINES[use_lcm] = build_pipeline(
            BASE_MODEL,
            resolved_lora_path,
            use_lcm=use_lcm,
        )

    return _PIPELINES[use_lcm]


def generate_from_prompt(
    prompt: str,
    negative_prompt: str | None = None,
    steps: int | None = None,
    guidance_scale: float | None = None,
    height: int | None = None,
    width: int | None = None,
    use_lcm: bool = USE_LCM,
    in_bucket: bool = False,
) -> str:
    pipe = get_pipeline(use_lcm=use_lcm)

    final_negative_prompt = (
        NEGATIVE_PROMPT if negative_prompt is None else negative_prompt
    )
    final_steps = STEPS if steps is None else steps
    final_guidance_scale = GUIDANCE_SCALE if guidance_scale is None else guidance_scale
    final_height = HEIGHT if height is None else height
    final_width = WIDTH if width is None else width

    return generate_image(
        pipe=pipe,
        prompt=prompt,
        negative_prompt=final_negative_prompt,
        output_dir=str(OUTPUT_DIR),
        num_inference_steps=final_steps,
        guidance_scale=final_guidance_scale,
        height=final_height,
        width=final_width,
        in_bucket=in_bucket,
    )


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:50]


def generate_and_upload(
    prompt: str,
    session_id: str,
    negative_prompt: str | None = None,
    steps: int | None = None,
    guidance_scale: float | None = None,
    height: int | None = None,
    width: int | None = None,
    use_lcm: bool = USE_LCM,
) -> dict:
    image = generate_from_prompt(
        prompt=prompt,
        negative_prompt=negative_prompt,
        steps=steps,
        guidance_scale=guidance_scale,
        height=height,
        width=width,
        use_lcm=use_lcm,
        in_bucket=True,
    )

    result = {"blob_path": None, "in_gcs": False}

    if INFERENCE_BUCKET:
        slug = slugify(prompt)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        blob_path = f"generation/{session_id}/{slug}-{timestamp}.png"
        upload_image_to_gcs(image, INFERENCE_BUCKET, blob_path)
        result["blob_path"] = blob_path
        result["in_gcs"] = True

    return result
