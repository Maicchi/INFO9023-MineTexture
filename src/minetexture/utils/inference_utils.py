import logging
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from google.cloud import storage
from PIL import Image


def download_file_from_gcs(gcs_uri: str, local_path: str) -> str:
    """
    Download a file from GCS to a local path
    """
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


def upload_image_to_gcs(image, bucket_name: str, blob_path: str) -> str:
    """
    Upload an image to GCS from memory and return the path
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    blob.upload_from_file(buffer, content_type="image/png")
    return f"gs://{bucket_name}/{blob_path}"


def remove_background(image):
    """
    Remove the background from an image
    """
    image = np.array(image)
    if image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

    mask = np.zeros(image.shape[:2], np.uint8)
    backgroundModel = np.zeros((1, 65), np.float64)
    foregroundModel = np.zeros((1, 65), np.float64)
    height, width = image.shape[:2]
    rect = (10, 10, width - 20, height - 20)

    cv2.grabCut(
        image, mask, rect, backgroundModel, foregroundModel, 5, cv2.GC_INIT_WITH_RECT
    )
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
    alpha = mask2 * 255
    b, g, r = cv2.split(image)
    result = cv2.merge([b, g, r, alpha])
    return Image.fromarray(result)


def name_datetime(model) -> datetime:
    """
    Extract a datetime from the model's display name (expecting format: {name}_{YYYYMMDD-HHMM}),
    """
    DATETIME_RE = re.compile(r"_(\d{8}-\d{4})$")
    m = DATETIME_RE.search(model.display_name or "")
    if m:
        try:
            return datetime.strptime(m.group(1), "%Y%m%d-%H%M")
        except ValueError:
            pass
    # Fallback: use Vertex AI creation time
    return (
        datetime.utcfromtimestamp(model.create_time.timestamp())
        if model.create_time
        else datetime.min
    )


def get_model_vertexai(
    project: str,
    region: str,
    model_name: str,
) -> str | None:
    """
    Look up the latest version of the specified model in Vertex AI Model Registry and return the GCS URI of its artifact.
    """
    try:
        from google.cloud import aiplatform
    except ImportError:
        logging.warning(
            "google-cloud-aiplatform not installed — skipping Vertex AI lookup."
        )
        return None

    try:
        aiplatform.init(project=project, location=region)

        all_models = aiplatform.Model.list(order_by="create_time desc")
        mine = [m for m in all_models if m.display_name.startswith(f"{model_name}_")]

        if not mine:
            logging.info(f"No Vertex AI models found starting with '{model_name}_'.")
            return None

        latest = max(mine, key=name_datetime)
        artifact_uri = latest.uri

        if not artifact_uri:
            logging.warning(f"Model '{latest.display_name}' has no artifact URI.")
            return None

        logging.info(
            f"Using Vertex AI model: '{latest.display_name}' (artifact_uri='{artifact_uri}')"
        )
        return find_safetensors_in_gcs_dir(artifact_uri)

    except Exception as exc:
        logging.warning(f"Could not reach Vertex AI Model Registry: {exc}")
        return None


def find_safetensors_in_gcs_dir(gcs_dir: str) -> str | None:
    """Return the gs:// URI of the first .safetensors file in a GCS directory."""
    if not gcs_dir.startswith("gs://"):
        return None

    no_prefix = gcs_dir.removeprefix("gs://")
    bucket_name, _, prefix = no_prefix.partition("/")
    prefix = prefix.rstrip("/")

    gcs_client = storage.Client()
    bucket = gcs_client.bucket(bucket_name)

    list_kwargs = {"prefix": prefix + "/"} if prefix else {}
    blobs = [
        b for b in bucket.list_blobs(**list_kwargs) if b.name.endswith(".safetensors")
    ]

    if not blobs:
        logging.warning(f"No .safetensors file found under GCS path: {gcs_dir}")
        return None

    return f"gs://{bucket_name}/{blobs[0].name}"
