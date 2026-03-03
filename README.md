# INFO9023---MineTexture: Minecraft texture generation system
An end-to-end MLOps system that learns Minecraft texture pack styles and generates new textures through a deployed cloud-based ML pipeline.

## Project overview
MineTexture is an end-to-end Machine learning system that learns the visual style of existing Minecraft texture packs and generates new textures based on the user requirement over the style.

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
├── data/
│   ├── raw/        # Original texture packs and their style.json
│   └── processed/      # Processed 512x512 textures
│
├── docs/
│   ├── CLOUD.md        # Cloud setup
│   ├── DATA_PROCESSING.md      # Data processing pipeline
│
├── scripts/
│   ├── process_textures.py
│   ├── uploading_to_gcs.py
│   ├── downloading_from_gcs.py
│   ├── EDA.ipynb
│   └── README.md       # scripts code utilisation explanation
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
│       ├── model/
│       │   ├── TO BE WRITTEN
│       │   └──
│       │
│       ├── utils/
│       │   └── dataset_utils.py        # utils functions for data processing pipeline
│       │
│       └── config/
│           └── data_settings.py        # configuration for data processing pipeline
│
├── tests/      # (future pytest tests)
│
├── ruff.toml
├── .gitignore
├── requirements.txt
├── .pre-commit-config.yaml
├── README.md
└── .github/workflows/      # CI/CD pipeline
```

## Sprint breakdown

### Sprint 1 - Project Organization
- Repository setup
- Gitflow
- CI/CD with Github actions
- Pre-commit hooks

### Sprint 2 - Data & Model Development
- EDA
- Texture preprocessing
- Model training
- Cloud storage integration

### Sprint 3 – API & Deployment
(Upcoming)
### Sprint 4 – Model Pipeline
(Upcoming)

### Sprint 5 – Dashboard
(Upcoming)

## Team
- GARDIER Simon s192580
- LIU Eléna s201772
- TRINH Camille s192024

## Documentation
For more detailed explanations, please refer to the `docs/` folder:
- [CLOUD.md](docs/CLOUD.md)
- [DATA_PROCESSING.md](docs/DATA_PROCESSING.md)
