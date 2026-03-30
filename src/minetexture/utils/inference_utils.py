from io import BytesIO
from pathlib import Path

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


def upload_image_to_gcs(image, bucket_name: str, blob_path: str) -> None:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    blob.upload_from_file(buffer, content_type="image/png")


def delete_image_from_gcs(bucket_name: str, blob_path: str) -> None:
    """Delete a blob from GCS."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.delete()


def stream_image_from_gcs(bucket_name: str, blob_path: str) -> bytes:
    """Download a blob from GCS as bytes (for streaming to browser)."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    buffer = BytesIO()
    blob.download_to_file(buffer)
    buffer.seek(0)
    return buffer.read()


def list_session_blobs(bucket_name: str, session_id: str) -> list[dict]:
    """List all blobs for a given session, sorted by upload time (most recent first)."""
    client = storage.Client()
    blobs = client.list_blobs(bucket_name, prefix=f"generation/{session_id}/")
    result = []
    for blob in blobs:
        result.append(
            {
                "blob_path": blob.name,
                "filename": blob.name.split("/")[-1],
                "updated": blob.updated,
            }
        )
    result.sort(key=lambda x: x["updated"] or "", reverse=True)
    return result
