# MineTexture: Minecraft texture generation system :sunflower:
An end-to-end MLOps system that learns Minecraft texture pack styles and generates new textures through a deployed cloud-based ML pipeline.

<div style="display: flex; justify-content: space-around; align-items: center;">
  <img src="misc/components.png" alt="Overall architecture" style="width: 90%;"/>
</div>

## Project overview
MineTexture is an end-to-end Machine learning system that learns the visual style of existing Minecraft texture packs and generates new textures based on the user prompt describing the style.

The system covers the complete MLOps lifecycle:
- Data preprocessing
- Model training
- Cloud storage
- API serving
- Docker deployment
- Model pipeline
- Dashboard interaction

## Project structure
```
INFO9023-MineTexture/
│
├── docs/
│   ├── CLOUD.md                # Cloud setup
│   ├── DATA_PROCESSING.md      # Data processing pipeline
│   ├── INFERENCE.md            # Inference service
│   ├── DASHBOARD.md            # API and front-end
│   └── TRAINING.md             # Model training
│
├── docker/
│   ├── Dockerfile.train
│   ├── Dockerfile.inference
|   └── Dockerfile.dashboard
│
├── scripts/
│   └── training/
|       ├── training.sh
|       └── training_config.toml
│   ├── model-experimentations.py
│   ├── process_textures.py
│   ├── uploading_to_gcs.py
│   ├── downloading_from_gcs.py
│   ├── EDA.ipynb
│   ├── test_inference_service.py
│   └── README.md
│
├── src/
│   └── minetexture/
|       ├── __init__.py
|       |
│       ├── dataset/
│       │   ├── image_processor.py
│       │   ├── caption_builder.py
│       │   ├── naming.py
│       │   └── style_info.py
│       │
│       ├── inference/
│       │   ├── api.py
│       │   ├── generator.py
│       │   └── service.py
│       │
│       ├── dashboard/
│       │   ├── core.py
│       │   |
│       │   ├── static/
│       │   │   ├── minecraft.css
│       │   │   └── images/                             # generation examples
│       │   │       ├── flower.png
│       │   │       ├── pickaxe.png
│       │   │       └── quartz.png
│       │   |
│       │   └── templates/
│       │       └── homepage.html
│       │
│       ├── database/
│       │
│       ├── web/
│       │
│       ├── utils/
│       │   ├── inference_utils.py
│       │   ├── dashboard_utils.py
│       │   └── dataset_utils.py
│       │
│       └── config/
│           ├── inference_settings.py
│           └── data_settings.py
│
├── tests/
│
├── ruff.toml
├── .gitignore
├── uv.lock
├── .pre-commit-config.yaml
├── README.md
├── .env-template
└── .github/workflows/                  # CI/CD pipeline
```
### :link: Links to our tools
- [Wandb](https://wandb.ai/s-gardier-work/minetexture)
- [Trello](https://trello.com/b/7UngPFV7/mlsd)
- [Google Cloud](https://console.cloud.google.com/welcome?authuser=1&project=info9023-minetexture)

## Sprint breakdown

### Sprint 1 - Project Organization
- :white_check_mark: Repository setup
- :white_check_mark: Gitflow
- :white_check_mark: CI/CD with Github actions
- :white_check_mark: Pre-commit hooks

### Sprint 2 - Data & Model Development
- :white_check_mark: EDA ([EDA notebook](scripts/EDA.ipynb))
- :white_check_mark: Texture preprocessing ([Data processing markdown](docs/DATA_PROCESSING.md))
- :white_check_mark: Model training ([Model training markdown](docs/TRAINING.md))
- :white_check_mark: Cloud storage integration ([Cloud storage markdown](docs/CLOUD.md))

### Sprint 3 – API & Deployment
- :white_check_mark: Build REST API to serve model + run locally ([Dashboard markdown](scripts/DASHBOARD.md))
- :white_check_mark: Package services in container ([Dashboard markdown](scripts/DASHBOARD.md))
- :white_check_mark: Deploy model serving in the Cloud ([Inference markdown](docs/INFERENCE.md))

### Sprint 4 – Model Pipeline
- :white_check_mark: Pipeline building ([Model training markdown](docs/TRAINING.md) + [Inference markdown](docs/INFERENCE.md))

### Sprint 5 – Dashboard
- :white_check_mark: Front-end rendered with Jinja2 and Minecraft CSS theme
- :white_check_mark: REST API with POST/GET/DELETE endpoints for texture management ([Dashboard markdown](scripts/DASHBOARD.md))
- :white_check_mark: Firestore integration for user authentication and image catalog
- :white_check_mark: Dashboard deployed to Cloud Run and publicly available ([Dashboard markdown](scripts/DASHBOARD.md))

### Sprint 6 – Connecting components & clean-up
- :white_check_mark: Renamed API routes to follow REST naming conventions ([Dashboard markdown](scripts/DASHBOARD.md))
- :white_check_mark: Background removal on generated images
- :white_check_mark: Inference loads the latest model from Vertex AI Model Registry, with fallback to GCS bucket model
- :white_check_mark: Automatic deployment of the inference service to Cloud Run on push to `develop` ([deploy.yml](.github/workflows/deploy.yml))
- :white_check_mark: Automatic deployment of the dashboard to Cloud Run on push to `develop` ([deploy.yml](.github/workflows/deploy.yml))

## Team
- GARDIER Simon s192580
- LIU Eléna s201772
- TRINH Camille s192024
