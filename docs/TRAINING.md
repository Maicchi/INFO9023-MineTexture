# 🧪 MineTexture Training (LoRA finetuning)
- The model is based on [Stable Diffusion 1.5](https://huggingface.co/Jiali/stable-diffusion-1.5) and fine-tuned with [kohya-ss/sd-scripts](https://github.com/kohya-ss/sd-scripts)
- Code related to model training can be found in the `scripts/training/` folder
- Docker image for training is available in: `docker/Dockerfile.train`

## Prerequisites
1. Create a copy of `INFO9023-MineTexture/.env-template`, rename it `.env`, edit it with valid paths, API keys,...
2. Download [Stable Diffusion 1.5](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5) to the folder referenced by `PRETRAINED_MODEL_PATH_HOST` in `.env`

## Training Run
Build and start the training Docker image:
```bash
cd INFO9023-MineTexture
docker build -f docker/Dockerfile.train -t minetexture-train .
docker run --env-file .env -e "GCS_SA_KEY_B64=$(base64 -w0 /ronflex/users/sgar@inno.evs.tv/credentials/gcs-sa-key.json)" --gpus all -v "${PRETRAINED_MODEL_PATH_HOST}:${PRETRAINED_MODEL_PATH_DOCKER}:ro" minetexture-train
```

> **Note:** Build takes ~6 min 30 s

## Checkpoints
Model checkpoints are stored in: `gs://training_data_minetexture/models/minetexture-checkpoints`
