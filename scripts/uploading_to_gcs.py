import argparse
import os

from google.cloud import storage
from tqdm import tqdm


def upload_folder_to_gcs(bucket_name, source_folder, destination_prefix=""):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    for root, _, files in os.walk(source_folder):
        for file_name in tqdm(
            files, desc="Uploading files content to GCS", unit="file"
        ):
            local_path = os.path.join(root, file_name)

            relative_path = os.path.relpath(local_path, source_folder)
            blob_path = os.path.join(destination_prefix, relative_path)
            blob_path = blob_path.replace("\\", "/")

            blob = bucket.blob(blob_path)
            blob.upload_from_filename(local_path)
    print("Upload completed.")


parser = argparse.ArgumentParser()
parser.add_argument(
    "--source",
    type=str,
    default="./processed",
    help="The source path of the folder containing all the packs you want to upload.",
)
args = parser.parse_args()

upload_folder_to_gcs(
    bucket_name="training_data_minetexture",
    source_folder=args.source,
    destination_prefix="",
)
