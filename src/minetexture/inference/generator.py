from __future__ import annotations

import os
import uuid
from pathlib import Path

import torch
from diffusers import LCMScheduler, StableDiffusionPipeline

from minetexture.utils.dashboard_utils import add_image_url_to_user
from minetexture.utils.inference_utils import (
    download_file_from_gcs,
    remove_background,
    upload_image_to_gcs,
)


def resolve_lora_path(lora_path: str) -> str:
    """Resolve the LoRA path, downloading from GCS if necessary"""
    if lora_path.startswith("gs://"):
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
    pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

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

    return pipe


def generate_image(
    pipe: StableDiffusionPipeline,
    prompt: str,
    user_id: str,
    output_dir: str,
    negative_prompt: str = "",
    num_inference_steps: int = 30,
    guidance_scale: float = 7.5,
    height: int = 512,
    width: int = 512,
    in_bucket: bool = False,
) -> str:
    """
    Run inference, generate unique ID for the image, save it to GCS + Firestore
    and return the path
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
    unique_filename = f"{uuid.uuid4()}.png"
    if in_bucket:
        bucket_name = "generated_data_minetexture"
        blob_path = f"generation/{unique_filename}"
        gcs_uri = upload_image_to_gcs(image, bucket_name, blob_path)
        add_image_url_to_user(user_id, gcs_uri)
        return gcs_uri
    else:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_path = os.path.join(output_dir, unique_filename)
        image.save(output_path)
        return output_path
