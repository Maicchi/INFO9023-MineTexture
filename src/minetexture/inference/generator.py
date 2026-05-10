from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

import torch
from diffusers import LCMScheduler, StableDiffusionPipeline

from minetexture.config.inference_settings import (
    VERTEX_AI_MODEL_NAME,
    VERTEX_AI_PROJECT,
    VERTEX_AI_REGION,
)
from minetexture.utils.inference_utils import (
    download_file_from_gcs,
    get_model_vertexai,
    remove_background,
)


def resolve_lora_path(lora_path: str) -> str:
    """
    Resolve the LoRA to a local file path:
    - the latesst loRA version from Vertex AI Model Registry (if configured)
    - otherwise, the specified GCS path or local path
    """
    # 1. Try Vertex AI artifact first
    if VERTEX_AI_PROJECT and VERTEX_AI_MODEL_NAME:
        vertex_uri = get_model_vertexai(
            project=VERTEX_AI_PROJECT,
            region=VERTEX_AI_REGION,
            model_name=VERTEX_AI_MODEL_NAME,
        )
        if vertex_uri:
            logging.info(f"[LoRA] Loading from Vertex AI artifact: {vertex_uri}")
            local_path = os.path.join(
                "data", "model", "tmp", os.path.basename(vertex_uri)
            )
            return download_file_from_gcs(vertex_uri, local_path)

        logging.warning(
            "[LoRA] Vertex AI artifact has no model yet — falling back to GCS bucket."
        )

    # 2. Fall back: download from GCS (or use the path as-is if already local)
    if lora_path.startswith("gs://"):
        logging.info(f"[LoRA] Loading from GCS bucket: {lora_path}")
        local_path = os.path.join("data", "model", "tmp", os.path.basename(lora_path))
        return download_file_from_gcs(lora_path, local_path)

    return lora_path


def build_pipeline(base_model: str, lora_path: str, use_lcm: bool = False):
    """
    Build the Stable Diffusion pipeline
        Input:  base model,
                specified LoRA and
                optional LCM integration
    """
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    pipe = StableDiffusionPipeline.from_pretrained(
        base_model,
        torch_dtype=dtype,
        safety_checker=None,
    )

    pipe.load_lora_weights(
        pretrained_model_name_or_path_or_dict=os.path.dirname(lora_path),
        weight_name=os.path.basename(lora_path),
        adapter_name="minetexture",
    )

    if use_lcm:
        pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
        pipe.load_lora_weights(
            "latent-consistency/lcm-lora-sdv1-5",
            adapter_name="lcm",
        )
        pipe.set_adapters(["minetexture", "lcm"], adapter_weights=[1.0, 1.0])
    else:
        pipe.set_adapters(["minetexture"], adapter_weights=[1.0])

    pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

    return pipe


def generate_image(
    pipe: StableDiffusionPipeline,
    prompt: str,
    output_dir: str,
    negative_prompt: str = "",
    num_inference_steps: int = 30,
    guidance_scale: float = 7.5,
    height: int = 512,
    width: int = 512,
    in_bucket: bool = False,
) -> str:
    """
    Run inference and either return the PIL image or save it to disk
    """
    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        height=height,
        width=width,
    )

    image = result.images[0]
    image = remove_background(image)
    if in_bucket:
        return image

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = os.path.join(output_dir, f"generated-{timestamp}.png")
    image.save(output_path)

    return output_path
