# Minetexture Dashboard 🖥️

## Overview
The dashboard is the web frontend of *MineTexture*. It is a Flask web application that lets a user:
- Enter a text prompt
- Display the generated texture image
- Look at generated textures from the session history
- Download and/or delete generated images from the Google Cloud Storage bucket

The dashboard does not generate images itself, it communicates with the `inference service` through HTTP that will handle texture generation.

## Architecture

### Utilisation flow
1. A user opens the web page
2. It creates a session UUID
3. The user sends a prompt using the form
4. The dashboard sends an authenticated HTTP request to the inference service
5. The inference service generates an image and stores it in GCS
6. The dashboard receives the image and shows it to the user
7. The user can download, delete the shown image from GCS or view a previously generated image

### Routes

| Route | Method | Description |
| --- | --- | --- |
| `/` | GET / POST | Homepage where it is possible to submit a prompt, view this session history,delete/download the generated textures |
| `/image` | GET | Stream a generated image from GCS |
| `/download` | GET | Download a generated texture from GCS |
| `/delete` | POST | Delete a generated image from GCS |

### Environment variables
| Variable | Default | Description |
|---|---|---|
| `INFERENCE_SERVICE_URL` | — | URL of the running Inference Service |
| `INFERENCE_API_KEY` | `secret` | Shared API key with the Inference Service |
| `INFERENCE_BUCKET` | `generated_data_minetexture` | GCS bucket where generated images are stored |
| `FLASK_SECRET_KEY` | `secret_key` | Flask session secret key |

### GCS Usage

Generated images are not stored locally, they are stored in a Google Cloud Storage bucket that both the dashboard and the inference service can access.

Each user session has its own prefix in the bucket and the images are structured as follows:
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
The dashboard can be run directly with Python:
```bash
python src/minetexture/dashboard/core.py
```
The built-in app runner starts on:
- host: `0.0.0.0`
- port: `8080`

The following are required:
- access to the configured GCS bucket
- valid Google Cloud credentials
- a reachable inference service at `INFERENCE_SERVICE_URL`
- the same `INFERENCE_API_KEY` configured on both services

### Docker Deployment
The container is defined in `docker/Dockerfile.dashboard`.

Build and run it with:
```bash
docker build -f docker/Dockerfile.dashboard -t minetexture-dashboard .
docker run --env-file .env -p 8080:8080 minetexture-dashboard
```

The `--env-file .env` flag passes all required environment variables including `INFERENCE_SERVICE_URL`, which must point to the port where the inference service is reachable (e.g. `http://localhost:8081`). (under the same docker network)

The app will then be accessible at `http://localhost:8080`.

### Cloud Deployment

First, tag and push the image to Google Artifact Registry:
```bash
docker tag minetexture-dashboard \
    europe-west1-docker.pkg.dev/info9023-minetexture/minetexture/dashboard:latest

docker push \
    europe-west1-docker.pkg.dev/info9023-minetexture/minetexture/dashboard:latest
```

Then deploy to Cloud Run:
```bash
gcloud run deploy dashboard \
    --image=europe-west1-docker.pkg.dev/info9023-minetexture/minetexture/dashboard:latest \
    --region=europe-west1 \
    --project=info9023-minetexture \
    --min-instances=0 \
    --memory=512Mi \
    --cpu=1 \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=info9023-minetexture,INFERENCE_SERVICE_URL=<INFERENCE_SERVICE_URL>,INFERENCE_API_KEY=<INFERENCE_API_KEY>,FLASK_SECRET_KEY=<FLASK_SECRET_KEY>" \
    --allow-unauthenticated
```

> **Note:** `INFERENCE_SERVICE_URL` should be the Cloud Run URL of the deployed inference service. `INFERENCE_API_KEY` and `FLASK_SECRET_KEY` should be set to secure values before deploying to production.
