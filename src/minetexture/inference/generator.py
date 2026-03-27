from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import torch
from diffusers import LCMScheduler, StableDiffusionPipeline
from google.cloud import storage


def download_file_from_gcs(gcs_uri: str, local_path: str) -> str:
    if not gcs_uri.startswith("gs://"):
        return gcs_uri

    no_prefix = gcs_uri.replace("gs://", "", 1)
    bucket_name, blob_path = no_prefix.split("/", 1)

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    Path(local_path).parent.mkdir(parents=True, exist_ok=True)
    blob.download_to_filename(local_path)
    return local_path


def resolve_lora_path(lora_path: str) -> str:
    if lora_path.startswith("gs://"):
        local_path = os.path.join("data", "model", "tmp", os.path.basename(lora_path))
        return download_file_from_gcs(lora_path, local_path)
    return lora_path


def build_pipeline(base_model: str, lora_path: str, use_lcm: bool = False):
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    pipe = StableDiffusionPipeline.from_pretrained(
        base_model,
        torch_dtype=dtype,
        safety_checker=None,
    )
    pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

    # Your MineTexture LoRA
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
    output_dir: str,
    negative_prompt: str = "",
    num_inference_steps: int = 30,
    guidance_scale: float = 7.5,
    height: int = 512,
    width: int = 512,
) -> str:
    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        height=height,
        width=width,
    )

    image = result.images[0]
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = os.path.join(output_dir, f"generated-{timestamp}.png")
    image.save(output_path)

    return output_path
