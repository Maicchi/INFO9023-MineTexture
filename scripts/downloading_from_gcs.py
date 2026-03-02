import argparse
import os

from google.cloud import storage
from tqdm import tqdm


def download_from_gcs(project_id, bucket_name, source_blob_name, destination_file_path):
    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)
    blobs = list(bucket.list_blobs())

    for blob in tqdm(blobs, desc="Downloading from GCS", unit="file"):
        if blob.name.endswith("/"):
            continue
        local_path = os.path.join(destination_file_path, *blob.name.split("/"))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        blob.download_to_filename(local_path)


parser = argparse.ArgumentParser()
parser.add_argument(
    "--dest",
    type=str,
    default="./train",
    help="The destination path where the packs will be saved.",
)
args = parser.parse_args()

download_from_gcs(
    project_id="217219593769",
    bucket_name="training_data_minetexture",
    source_blob_name="",
    destination_file_path=args.dest,
)
