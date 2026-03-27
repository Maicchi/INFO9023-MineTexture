from __future__ import annotations

from minetexture.config.inference_settings import (
    BASE_MODEL,
    GUIDANCE_SCALE,
    HEIGHT,
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
    )
