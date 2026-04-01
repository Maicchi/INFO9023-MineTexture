# Google Cloud ☁️

## Initial set up
As we configured it during the lab, you should have access to the project.
To check, you can **list all of your projects**:
```
gcloud projects list
```
You should see the minetexture project:
`
PROJECT_ID NAME PROJECT_NUMBER ENVIRONMENT
`
`
info9023-minetexture     INFO9023-Minetexture  217219593769
`

You can then **set it** as your main project:
```
gcloud config set project 217219593769
```
And **check** if you're in the correct project:
```
gcloud config get-value project
```

## Data storage
Since our project is composed of:
- Training data: images and their labels
- ML pre-trained models for image generation
- Output: images + information on the output

It will be more interesting to use Google Cloud Storage (GCS) and for the output, use GCS for the images and the main structure in Firestore.

### Buckets (GCS)
#### Training dataset
A bucket "training_data_minetexture" following this structure:
```
training-data-minetexture/
├── data_training/
│   └── images/
│        ├── pack_name-category_item_name.png
│        ├── pack_name-category_item_name.txt
│        └── ...
└── labels.csv
```
Python scripts can be found in /scripts to upload textures packs into the bucket and download them from the bucket.

#### Output images
Generated images are stored following this structure:
```
generated_data_minetexture/
├── generation/
│   ├── <session_id>/
│   │   ├── <slug>-<timestamp>.png
    │   └── ...
│   └── ....
└── ...
```
The slug is derived from the prompt used to generate the image.

### Collection (Firestore)
In the case of a generation of a whole texture pack, a collection "output-minetexture" following this structure could be use :
```
output-minetexture:{                    // Collection
    pack_id:{                           // Document
        "name"
        "nb files left to process"
        "zip uri"
        "status"    // in queue, processing, done
        "createdAt"
        "updatedAt"
        images:{                        // Sub-collection
            "image_0001"{               // Document
                "filename"
                "image_url" // gcs uri
                "createdAt"
            }
        }
    }
}
```

A python script will be found in /scripts to handle user requests to create a pack as well as updating its information when image are generated.

## References
Adapted the lab 2 from the MSLD course:
https://github.com/ThomasVrancken/info9023-mlops/blob/main/directed_work/02_cloud_data/README.md
