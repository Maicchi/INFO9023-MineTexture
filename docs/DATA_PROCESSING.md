# Data Processing Pipeline

## Overview
This document describes the dataset processing pipeline used to transform raw Minecraft texture packs into a structured dataset suitable for machine learning tasks.

The pipeline performs the following operations:

- Scans raw resource packs
- Extracts and preprocesses texture images
- Normalizes transparency and image size
- Generates descriptive captions
- Produces a summary `labels.csv` metadata file for data exploration

The objective is to convert heterogeneous resource pack structures into a consistent, reproducible dataset ready for training and experimentation.

## Input data structure
Raw data are placed under:
```
data/raw
```
Each resource pack must follow the Minecraft resource pack structure and include a `style.json` file:
```
data/raw/
| resource_pack_name/
| | style.json
| | assets/
| | | minecraft/
| | | | textures/
| | | | | block/
| | | | | item/
| | | | | entity/
| | | | | gui/
```
The file `style.json` defines:
- `texture_pack_name`: pack identifier
- `style`: style name
- `keywords`: style related keywords
- `texture_path`: (optional) mod namespace for non-vanilla packs

Only packs containing a valid `style.json` file are processed.

## Output data structure
Processed data are stored under:
```
data/processed/
```
Each processed texture produces:
- A normalized `.png` image
- A corresponding `.txt` caption file
- An entry in `labels.csv`

Example structure:
```
data/processed/
| packName-kind_texture.png
| packName-kind_texture.txt
| labels.csv
```
