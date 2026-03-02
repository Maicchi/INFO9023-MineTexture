# Google Cloud

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

It will be more interesting to use Google Cloud Storage (GCS) and for the output, combine it with CloudSQL.

### File tree
**Training dataset**:
train/
| &nbsp; labels.csv
| &nbsp; ressource_pack_1_name/
| &nbsp; | &nbsp; category_name/
| &nbsp; | &nbsp; | &nbsp; item_1_name.png
| &nbsp; | &nbsp; | &nbsp; item_1_name.txt
Where the label.csv will contain the path, the main style and the category of the item for each item from all packs.

**Output**:
Output/
| &nbsp; ID_output
Where the ID_output is a firestore database file that will be structured like this:
ID_output:{
 &nbsp; remaining:{"name_folder/name_2_item.png", ...}
 &nbsp; done:{"name_folder/name_1_item.png" : object<image_url, ...}
 &nbsp; pack: .zip
 &nbsp; pack:id
 &nbsp; pack:name
}
Where the images_url is an url to the image generated which will be stored in a GCS bucket, as well as the .zip.

### Buckets
We have:
- A bucket "training_data_minetexture" following the training dataset file tree.
- A bucket "output_data_mintexture" containing the images generated.

## References
Adapted the lab 2 from the MSLD course:
https://github.com/ThomasVrancken/info9023-mlops/blob/main/directed_work/02_cloud_data/README.md
