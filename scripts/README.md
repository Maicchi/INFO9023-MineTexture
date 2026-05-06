# Scripts
Brief description on how to use them.

#### uploading_to_gcs.py
To be used at the root where there is a folder which contains all the packs to be uploaded.
To call it : `python scripts/uploading_to_gcs.py --source ./YourFolderSourcePath`
By default the source path of the folder is ./processed

#### downloading_from_gcs.py
Download the packs from google cloud storage and (create and) put into a local folder the packs.
To call it : `python scripts/downloading_from_gcs.py --dest ./YourFolderDestinationPath`
By default the destination path of the folder is ./train

#### process_textures.py
Process raw Minecraft texture packs into a structured dataset.
This script:
- Scans raw resource packs
- Preprocesses images (RGBA normalization, transparency handling, resizing)
- Generates captions
- Exports `labels.csv` (used for EDA)
To call it from the project root:  `python ./scripts/process_textures.py`
Optional arguments:
`python -m scripts.process_textures --raw-dir ./data/raw --processed-dir ./data/processed`
By default:
- Raw directory: `./data/raw`
- Processed directory: `./data/processed`

#### test_inference_service.py
Run a local test of the inference service by generating one texture image from a given prompt.
This script:
- calls `generate_from_prompt` of `service.py`
- prints the path of the generated image
To call it from the project root: `python scripts/test_inference_service.py`
Optional arguments:
- `--prompt`: text prompt for generation
    *(default: "minecraft stone texture, pixel art, seamless, game asset")*
- `--negative-prompt`: a negative prompt for unwanted features
- `--steps`: number of inference steps
    *(default: 30)*
- `--guidance-scale`: guidance scale
    *(default: 7.5)*
- `--use-lcm`: enable LCM inference mode (for experimentations)
    *(default: False)*
- `--height`: output image height
    *(default: 512)*
- `--width`: output image width
    *(default: 512)*
