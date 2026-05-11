import os
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
    add_image_url_to_user,
    delete_image_firestore,
    delete_image_from_gcs,
    handle_auth,
    list_user_images,
    stream_image_from_gcs,
)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "secret_key")
API_KEY = os.getenv("INFERENCE_API_KEY", "secret")

OUTPUT_DIR_ABS = os.path.abspath(OUTPUT_DIR)
INFERENCE_SERVICE_URL = os.getenv("INFERENCE_SERVICE_URL")


def call_inference_service(prompt: str, user_id: str) -> dict:
    """
    Send a generation request to the inference service
    """
    response = httpx.post(
        f"{INFERENCE_SERVICE_URL}/textures",
        json={"prompt": prompt, "user_id": user_id},
        headers={"X-API-Key": API_KEY},
        timeout=600.0,  # withut GPU: +-9min
    )
    response.raise_for_status()
    return response.json()


# Flask routes for the dashboard
# Home page
@app.route("/", methods=["GET", "POST"])
def home_page():
    """ "
    Main dashboard page:
    Handles image generation requests
    """
    user_id = session.get("user_id")

    if request.method == "POST" and user_id:
        input_prompt = request.form.get("prompt")
        if input_prompt:
            result = call_inference_service(input_prompt, user_id)
            if result["in_gcs"] and result["blob_path"]:
                add_image_url_to_user(user_id, result["blob_path"])
                return redirect(url_for("home_page", selected_blob=result["blob_path"]))
        return redirect(url_for("home_page"))

    selected_blob = request.args.get("selected_blob")
    generated_image = selected_blob is not None
    blob_path = selected_blob if selected_blob else None
    if user_id:
        session_images = list_user_images(user_id)
    else:
        session_images = []

    return render_template(
        "homepage.html",
        generated_image=generated_image,
        blob_path=blob_path,
        session_images=session_images,
    )


# Log in / account creation page
@app.route("/session", methods=["GET", "POST", "DELETE"])
def handle_session():
    """ "
    Login page:
    Handles user authentication requests
    """
    if request.method == "DELETE":
        session.clear()
        return {"redirect": url_for("handle_session")}

    user_id = session.get("user_id")
    if user_id:
        return redirect(url_for("home_page"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        auth_result = handle_auth(username, password)

        if auth_result["status"] in ["success", "created"]:
            session["user_id"] = auth_result["user_id"]
            session["username"] = username
            return redirect(url_for("home_page"))
        else:
            return "Invalid Login", 401

    return render_template("login.html")


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
    user_id = session.get("user_id")
    if blob_path:
        delete_image_from_gcs(INFERENCE_BUCKET, blob_path)
        delete_image_firestore(user_id, blob_path)
    selected_blob = request.args.get("selected_blob")
    if selected_blob and selected_blob == blob_path:
        return {"redirect": url_for("home_page")}
    return {
        "redirect": url_for("home_page", selected_blob=selected_blob)
        if selected_blob
        else url_for("home_page")
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)
