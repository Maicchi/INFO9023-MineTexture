#!/usr/bin/env python3
"""
Script to process Minecraft texture packs.
"""

import argparse
from pathlib import Path

from minetexture.config.data_settings import DEFAULT_PROCESSED_DIR, DEFAULT_RAW_DIR
from minetexture.dataset.image_processor import TextureProcessor


def main():
    parser = argparse.ArgumentParser(description="Process Minecraft texture packs")
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=DEFAULT_RAW_DIR,
        help="Directory containing raw texture packs",
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=DEFAULT_PROCESSED_DIR,
        help="Directory to save processed textures",
    )

    args = parser.parse_args()

    processor = TextureProcessor(
        raw_path=args.raw_dir, processed_path=args.processed_dir
    )
    processor.process()


if __name__ == "__main__":
    main()
