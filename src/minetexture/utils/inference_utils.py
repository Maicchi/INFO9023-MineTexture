from io import BytesIO
from pathlib import Path

from google.cloud import storage


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


def upload_image_to_gcs(image, bucket_name: str, blob_path: str) -> None:
    """
    Upload an image to GCS from memory
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    blob.upload_from_file(buffer, content_type="image/png")
