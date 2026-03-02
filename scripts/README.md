# Scripts
Brief description on how to use them.

#### uploading_to_gcs.py
To be used at the root where there is a folder which contains all the packs to be uploaded.
To call it : `python uploading_to_gcs.py --source ./YourFolderSourcePath`
By default the source path of the folder is ./processed

#### downloading_from_gcs.py
Download the packs from google cloud storage and (create and) put into a local folder the packs.
To call it : `python downloading_from_gcs.py --dest ./YourFolderDestinationPath`
By default the destination path of the folder is ./train
