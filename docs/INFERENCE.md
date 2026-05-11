# Minetexture Inference Service ⚙️

## Overview
The inference service is the backend of *MineTexture*. It is a FastAPI service that:
- receives a generation prompt from the dashboard
- loads a fine-tuned LoRA model from GCS or reuses a cached one
- generates a Minecraft texture image
- uploads the PNG to a GCS bucket
- returns the blob path to the caller

The inference service does not serve images to the user directly, it communicates with the `dashboard` which handles the web frontend.

## Architecture

### Utilisation flow
1. The dashboard sends an authenticated POST request with a prompt and a session ID
2. The service loads (or reuses a cached) fine-tuned pipeline
3. The service generates one texture image from the prompt
4. The generated PNG is uploaded to GCS
5. The blob path is returned to the dashboard

### Generation pipeline
The service supports 2 modes:
- **Standard mode:** base Stable Diffusion 1.5 + MineTexture trained LoRA
- **LCM mode:** base Stable Diffusion 1.5 + MineTexture LoRA + LCM scheduler pre-trained LoRA

> **Note:** LCM mode is currently used for experimentation and may later be replaced with a MineTexture-trained LCM LoRA.

### API

#### `POST /generate`
Generates a texture from a text prompt and uploads it to GCS.

**Headers:**
```
X-API-Key: <INFERENCE_API_KEY>
```
The API key is used to authenticate requests and must match the key configured on the dashboard side.

**Request body:**
```json
{
  "prompt": "Steampunk purple hat",
  "session_id": "<uuid>",
  "steps": 30,
  "guidance_scale": 7.5,
  "use_lcm": false
}
```

**Response:**
```json
{
  "blob_path": "generation/<session_id>/<slug>-<timestamp>.png",
  "in_gcs": true
}
```

### Environment variables

#### Model source (Vertex AI — primary)
| Variable | Default | Description |
|---|---|---|
| `VERTEX_AI_PROJECT` | `info9023-minetexture` | GCP project where the Vertex AI Model Registry lives |
| `VERTEX_AI_REGION` | `europe-west1` | GCP region of the Vertex AI Model Registry |
| `VERTEX_AI_MODEL_NAME` | `minetexture-lora` | Base display name of the registered model. The service looks for models named `{VERTEX_AI_MODEL_NAME}_YYYYMMDD-HHMM` and picks the most recent one. |

#### Model source (GCS — fallback)
| Variable | Default | Description |
|---|---|---|
| `LORA_PATH` | `gs://minetexture-checkpoints/Minecraft-Textures.safetensors` | GCS URI used as fallback when no model is found in the Vertex AI artifact |

#### Generation
| Variable | Default | Description |
|---|---|---|
| `BASE_MODEL` | `runwayml/stable-diffusion-v1-5` | Base Stable Diffusion model |
| `STEPS` | `30` | Number of diffusion steps |
| `GUIDANCE_SCALE` | `7.5` | Classifier-free guidance scale |
| `HEIGHT` | `512` | Output image height in pixels |
| `WIDTH` | `512` | Output image width in pixels |
| `NEGATIVE_PROMPT` | `""` | Negative prompt |
| `USE_LCM` | `false` | Use LCM scheduler (experimental) |

#### API & storage
| Variable | Default | Description |
|---|---|---|
| `INFERENCE_API_KEY` | `secret` | API key required in the `X-API-Key` header |
| `INFERENCE_BUCKET` | `generated_data_minetexture` | GCS bucket where generated images are uploaded |
| `OUTPUT_DIR` | `data/output` | Local fallback output directory |

### GCS Usage
Generated images are uploaded to the bucket `generated_data_minetexture`. Each session has its own prefix and the images are structured as follows:
```
generated_data_minetexture/
└── generation/
    └── <session_id>/
        ├── <slug>-<timestamp>.png
        └── ...
```
The slug is derived from the prompt used to generate the image.

## Running

### Local Execution
The inference service can be tested through the script `scripts/test_inference_service.py` without running the full stack:
```bash
python scripts/test_inference_service.py
```
The following are required:
- a GPU (CPU fallback is supported but very slow — ~9 min per image)
- valid Google Cloud credentials
- a reachable LoRA checkpoint at `LORA_PATH`

### Docker Deployment
The container is defined in `docker/Dockerfile.inference`.

Both the dashboard and the inference service must run on the same Docker network so they can communicate with each other. First, create a shared network:
```bash
docker network create minetexture-network
```

Then start the inference service on that network:
```bash
docker build -f docker/Dockerfile.inference -t minetexture-inference .
docker run --env-file .env --gpus all -p 8081:8080 --network minetexture-network --name minetexture-inference minetexture-inference
```

Then start the dashboard, pointing `INFERENCE_SERVICE_URL` to the inference container name:
```bash
docker build -f docker/Dockerfile.dashboard -t minetexture-dashboard .
docker run --env-file .env -p 8080:8080 --network minetexture-network --name minetexture-dashboard -e INFERENCE_SERVICE_URL=http://minetexture-inference:8080 minetexture-dashboard
```

Within a Docker network, containers reach each other by **container name** rather than `localhost`. The `-e INFERENCE_SERVICE_URL=http://minetexture-inference:8080` overrides whatever is set in `.env` for that variable.

The dashboard will then be accessible at `http://localhost:8080`.

### Cloud Deployment

First, tag and push the image to Google Artifact Registry:
```bash
docker tag minetexture-inference \
    europe-west1-docker.pkg.dev/info9023-minetexture/minetexture/inference:latest

docker push \
    europe-west1-docker.pkg.dev/info9023-minetexture/minetexture/inference:latest
```

Then deploy to Cloud Run:
```bash
gcloud run deploy inference \
    --image=europe-west1-docker.pkg.dev/info9023-minetexture/minetexture/inference:latest \
    --region=europe-west1 \
    --project=info9023-minetexture \
    --gpu=1 \
    --gpu-type=nvidia-l4 \
    --no-cpu-throttling \
    --min-instances=0 \
    --max-instances=1 \
    --memory=16Gi \
    --cpu=4 \
    --timeout=300 \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=info9023-minetexture, VERTEX_AI_PROJECT=info9023-minetexture, VERTEX_AI_REGION=europe-west1, VERTEX_AI_MODEL_NAME=minetexture-lora, LORA_PATH=gs://minetexture-checkpoints/Minecraft-Textures.safetensors, INFERENCE_API_KEY=<INFERENCE_API_KEY>" \
    --allow-unauthenticated
```

> **Note:** `INFERENCE_API_KEY` should be set to a secure value before deploying to production. It must match the key configured on the dashboard side.
> The service will first look for the latest model registered in Vertex AI Model Registry under the name `minetexture-lora_YYYYMMDD-HHMM`. If none is found, it falls back to `LORA_PATH`.

### Continuous Deployment (CI/CD)

The inference service is automatically built and deployed to Cloud Run when a push is made to the `develop` branch **and** at least one of the following files has changed:

| Path | Reason |
|---|---|
| `src/minetexture/inference/**` | Inference service source code |
| `src/minetexture/utils/inference_utils` | Inference utility functions |
| `src/minetexture/config/inference_settings.py` | Inference configuration and settings |
| `docker/Dockerfile.inference` | Inference container definition |
| `pyproject.toml` | Project dependencies |
| `uv.lock` | Locked dependency versions |

The pipeline (`.github/workflows/cd.yml`) runs these steps in order:
1. **Build** the Docker image from `docker/Dockerfile.inference`
2. **Tag** the image with `:latest` and the commit SHA
3. **Push** the image to Google Artifact Registry (`europe-west1-docker.pkg.dev/info9023-minetexture/minetexture/inference`)
4. **Deploy** the new image to the `inference` Cloud Run service

A manual deployment can also be triggered at any time from the GitHub Actions tab, with the option to deploy `inference`, `dashboard`, or `both`.
