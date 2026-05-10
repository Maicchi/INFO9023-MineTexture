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
