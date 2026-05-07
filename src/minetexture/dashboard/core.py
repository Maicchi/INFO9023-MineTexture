import os
import uuid
from io import BytesIO

import httpx
from flask import (
    Flask,
    Response,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from minetexture.config.inference_settings import (
    INFERENCE_BUCKET,
    OUTPUT_DIR,
)
from minetexture.utils.dashboard_utils import (
    delete_image_from_gcs,
    list_session_blobs,
    stream_image_from_gcs,
)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "secret_key")
API_KEY = os.getenv("INFERENCE_API_KEY", "secret")

OUTPUT_DIR_ABS = os.path.abspath(OUTPUT_DIR)
INFERENCE_SERVICE_URL = os.getenv("INFERENCE_SERVICE_URL")


def call_inference_service(prompt: str, session_id: str) -> dict:
    """
    Send a generation request to the inference service
    """
    response = httpx.post(
        f"{INFERENCE_SERVICE_URL}/textures",
        json={"prompt": prompt, "session_id": session_id},
        headers={"X-API-Key": API_KEY},
        timeout=600.0,  # withut GPU: +-9min
    )
    response.raise_for_status()
    return response.json()


@app.route("/", methods=["GET", "POST"])
def home_page():
    """ "
    Main dashboard page:
    Handles image generation requests
    """
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    session_id = session["session_id"]

    if request.method == "POST":
        input_prompt = request.form.get("prompt")
        if input_prompt:
            result = call_inference_service(input_prompt, session_id)
            if result["in_gcs"] and result["blob_path"]:
                return redirect(url_for("home_page", selected_blob=result["blob_path"]))
        return redirect(url_for("home_page"))

    selected_blob = request.args.get("selected_blob")
    generated_image = selected_blob is not None
    blob_path = selected_blob if selected_blob else None
    session_images = (
        list_session_blobs(INFERENCE_BUCKET, session_id) if INFERENCE_BUCKET else []
    )

    return render_template(
        "homepage.html",
        generated_image=generated_image,
        blob_path=blob_path,
        session_images=session_images,
    )


@app.route("/image")
def serve_gcs_image():
    """
    Stream an image from GCS in the dashboard
    """
    blob_path = request.args.get("blob_path")
    if not blob_path:
        return "No blob path provided", 400
    image_bytes = stream_image_from_gcs(INFERENCE_BUCKET, blob_path)
    return Response(image_bytes, mimetype="image/png")


@app.route("/image/file")
def image_file():
    """
    Download an image from GCS in the dashboard
    """
    blob_path = request.args.get("blob_path")
    if not blob_path:
        return "No blob path provided", 400
    image_bytes = stream_image_from_gcs(INFERENCE_BUCKET, blob_path)
    filename = blob_path.split("/")[-1]
    return send_file(
        BytesIO(image_bytes),
        mimetype="image/png",
        as_attachment=True,
        download_name=filename,
    )


@app.route("/image", methods=["DELETE"])
def delete_gcs_image():
    blob_path = request.args.get("blob_path")
    if blob_path:
        delete_image_from_gcs(INFERENCE_BUCKET, blob_path)
    selected_blob = request.args.get("selected_blob")
    if selected_blob and selected_blob == blob_path:
        return {"redirect": url_for("home_page")}
    return {
        "redirect": url_for("home_page", selected_blob=selected_blob)
        if selected_blob
        else url_for("home_page")
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)
