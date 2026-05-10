import hashlib
from io import BytesIO

from google.cloud import firestore, storage


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


def get_user_id(username):
    "Get the user ID by hashing the username"
    return hashlib.sha256(username.lower().encode()).hexdigest()


def handle_auth(username, password):
    """Handle user authentication:
    - Log in: If username exists and password is correct
    - Create account: if not already existing
    """
    user_id = get_user_id(username)
    db = firestore.Client(database="users-minetexture")
    user_ref = db.collection("users-minetexture").document(user_id)
    user_doc = user_ref.get()

    password_hash = hashlib.sha256(password.encode()).hexdigest()

    if user_doc.exists:  # Log in user if exists and password is correct
        if user_doc.to_dict()["password_hash"] == password_hash:
            return {"status": "success", "user_id": user_id}
        else:
            return {"status": "error"}
    else:  # Create new user in db
        user_ref.set({"username": username, "password_hash": password_hash})
        return {"status": "created", "user_id": user_id}


def add_image_url_to_user(user_id: str, blob_path: str) -> None:
    """Add a generated image entry to the user's 'images' subcollection."""
    db = firestore.Client(database="users-minetexture")
    user_ref = db.collection("users-minetexture").document(user_id)
    images_col = user_ref.collection("images")
    images_col.add(
        {
            "blob_path": blob_path,
            "filename": blob_path.split("/")[-1],
            "created_at": firestore.SERVER_TIMESTAMP,
        }
    )


def list_user_images(user_id: str) -> list[dict]:
    """List images stored in the user's 'images' subcollection, newest first."""
    db = firestore.Client(database="users-minetexture")
    images = (
        db.collection("users-minetexture")
        .document(user_id)
        .collection("images")
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .stream()
    )

    result = []
    for doc in images:
        d = doc.to_dict()
        result.append(
            {
                "blob_path": d.get("blob_path"),
                "filename": d.get("filename"),
                "updated": d.get("created_at"),
            }
        )
    return result


def delete_image_firestore(user_id: str, blob_path: str) -> None:
    """Find and delete the document matching the blob_path."""
    db = firestore.Client(database="users-minetexture")

    docs = (
        db.collection("users-minetexture")
        .document(user_id)
        .collection("images")
        .where("blob_path", "==", blob_path)
        .stream()
    )

    for doc in docs:
        doc.reference.delete()
