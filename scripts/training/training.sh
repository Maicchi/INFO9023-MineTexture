#!/bin/bash
set -euo pipefail
set -x
export RUN_TIMESTAMP="$(date +%Y%m%d-%H%M)"

gcloud_authenticate() {
  if ! command -v gcloud &> /dev/null; then
    echo "gcloud CLI not found"
    exit 1
  fi

  if [[ -n "${GCS_SA_KEY_B64:-}" ]]; then
    export GOOGLE_APPLICATION_CREDENTIALS="$(mktemp /tmp/gcs_sa_key_XXXXXX.json)"
    echo "${GCS_SA_KEY_B64}" | base64 -d > "${GOOGLE_APPLICATION_CREDENTIALS}"
    echo "Decoded GCS_SA_KEY_B64 to GOOGLE_APPLICATION_CREDENTIALS"
  fi

  if [[ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" ]]; then
    echo "Using service account key for Google Cloud Auth"
    gcloud auth activate-service-account --key-file="${GOOGLE_APPLICATION_CREDENTIALS}"
  else
    echo "Using Application Default Credentials"
  fi
}
if [[ -n "${GCS_DATASET_BUCKET:-}" || -n "${GCS_CHECKPOINTS_BUCKET:-}" ]]; then
  gcloud_authenticate
fi

# Download training data
if [[ -n "${GCS_DATASET_BUCKET:-}" ]]; then
  echo "Syncing dataset: ${GCS_DATASET_BUCKET} -> ${TRAINING_DATASET_PATH}"
  mkdir -p "${TRAINING_DATASET_PATH}"
  gcloud storage rsync "${GCS_DATASET_BUCKET}" "${TRAINING_DATASET_PATH}" --recursive
  echo "Dataset ready ($(find "${TRAINING_DATASET_PATH}" -type f | wc -l) files)"
fi

# Download base model from Hugging Face
if [[ -f "${PRETRAINED_MODEL_PATH_DOCKER}/model_index.json" ]]; then
  echo "Model present at ${PRETRAINED_MODEL_PATH_DOCKER}, skipping download"
else
  echo "Downloading Remote ${HF_MODEL_REPO} in Local ${PRETRAINED_MODEL_PATH_DOCKER}"
  mkdir -p "${PRETRAINED_MODEL_PATH_DOCKER}"
  hf download "${HF_MODEL_REPO}" \
    --local-dir "${PRETRAINED_MODEL_PATH_DOCKER}" \
    --exclude "*.bin" "*.ckpt" "*.pt"
  echo "Downloaded $(find "${PRETRAINED_MODEL_PATH_DOCKER}" -type f | wc -l) files"
fi

# Training config
TRAINING_CONFIG="$(mktemp /tmp/training_config_XXXXXX.toml)"
ACCELERATE_CONFIG="$(mktemp /tmp/accelerate_config_XXXXXX.yaml)"
trap 'rm -f "${TRAINING_CONFIG}" "${ACCELERATE_CONFIG}"' EXIT
envsubst < "/app/training_config.toml" > "${TRAINING_CONFIG}"
cat > "${ACCELERATE_CONFIG}" <<EOF
compute_environment: LOCAL_MACHINE
distributed_type: MULTI_GPU
num_processes: ${NUM_PROCESSES}
num_machines: ${NUM_MACHINES}
mixed_precision: "${MIXED_PRECISION}"
dynamo_config:
  dynamo_backend: "${DYNAMO_BACKEND}"
EOF

# Training run
mkdir -p "${MINETEXTURE_CHECKPOINTS_OUTPUT_FOLDER_PATH}/${RUN_TIMESTAMP}"
cd /app/sd-scripts
accelerate launch \
  --config_file="${ACCELERATE_CONFIG}" \
  train_network.py \
  --config_file="${TRAINING_CONFIG}" \
  --wandb_run_name="minetexture-lora_${LORA_DIM}-${INPUT_DIM}-${RUN_TIMESTAMP}"

# Checkpoints upload
if [[ -n "${GCS_CHECKPOINTS_BUCKET:-}" ]]; then
  LOCAL_CKPT_DIR="${MINETEXTURE_CHECKPOINTS_OUTPUT_FOLDER_PATH}/${RUN_TIMESTAMP}"
  REMOTE_CKPT_DIR="${GCS_CHECKPOINTS_BUCKET}/${RUN_TIMESTAMP}"
  echo "Uploading checkpoints: ${LOCAL_CKPT_DIR} -> ${REMOTE_CKPT_DIR}"
  gcloud storage rsync "${LOCAL_CKPT_DIR}" "${REMOTE_CKPT_DIR}" --recursive
  echo "Checkpoints uploaded ($(find "${LOCAL_CKPT_DIR}" -type f | wc -l) files)"
fi
