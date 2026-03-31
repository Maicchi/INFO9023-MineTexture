from io import BytesIO

from google.cloud import storage


def delete_image_from_gcs(bucket_name: str, blob_path: str) -> None:
    """Delete an image from GCS."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.delete()


def stream_image_from_gcs(bucket_name: str, blob_path: str) -> bytes:
    """Download an image from GCS as bytes (for streaming to browser)."""
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
