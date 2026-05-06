import os

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from minetexture.inference.service import generate_and_upload

app = FastAPI()

API_KEY = os.getenv("INFERENCE_API_KEY", "secret")


class GenerateRequest(BaseModel):
    """
    Request model for image generation
    """

    prompt: str
    session_id: str
    steps: int | None = None
    guidance_scale: float | None = None
    use_lcm: bool = False


@app.post("/generate")
def generate(req: GenerateRequest, x_api_key: str | None = Header(default=None)):
    """
    API endpoint to generate an image from a prompt
    """
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    result = generate_and_upload(
        prompt=req.prompt,
        session_id=req.session_id,
        steps=req.steps,
        guidance_scale=req.guidance_scale,
        use_lcm=req.use_lcm,
    )
    return result  # {"blob_path": "...", "in_gcs": True}


@app.get("/health")
def health():
    """
    Health check endpoint
    """
    return {"status": "ok"}
