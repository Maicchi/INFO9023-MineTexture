from __future__ import annotations

import csv
from pathlib import Path

from minetexture.config.data_settings import (
    DEFAULT_PROCESSED_DIR,
    DEFAULT_RAW_DIR,
    MINECRAFT_TEXTURE_PATHS,
)
from minetexture.dataset.caption_builder import CaptionBuilder
from minetexture.dataset.naming import TextureNamer
from minetexture.dataset.style_info import StyleInfo
from minetexture.utils.dataset_utils import (
    ensure_dir_exists,
    list_images,
    process_image,
)


class TextureProcessor:
    """Build a processed texture dataset from raw Minecraft texture packs"""

    def __init__(
        self,
        raw_path: Path = DEFAULT_RAW_DIR,
        processed_path: Path = DEFAULT_PROCESSED_DIR,
    ):
        self.raw_path = raw_path
        self.processed_path = processed_path
        self.namer = TextureNamer()
        self.caption_builder = CaptionBuilder()
        # file, labels, pack, style, kind
        self.labels: list[tuple[str, str, str, str, str]] = []

    def process(self) -> None:
        """Process all texture packs in the raw directory"""
        for pack_dir in sorted(p for p in self.raw_path.iterdir() if p.is_dir()):
            self._process_pack(pack_dir)

        self._write_labels_csv()
        print(f"[done] wrote labels.csv with {len(self.labels)} rows")

    def _process_pack(self, pack_dir: Path) -> None:
        """Process a single texture pack directory into processed path"""
        style = self._load_style_info(pack_dir)
        if not style:
            print(f"[skip] {pack_dir.name}: missing or invalid style.json")
            return

        total = 0
        scan_paths = list(MINECRAFT_TEXTURE_PATHS)
        modid = getattr(style, "texture_path", None)

        if modid:
            mod_root = pack_dir / "assets" / modid
            if not mod_root.exists():
                print(
                    f"[warning] {pack_dir.name}: assets/{modid} does not exist (from texture_path='{modid}')"
                )
            else:
                for cfg_path in MINECRAFT_TEXTURE_PATHS:
                    if not cfg_path.startswith("assets/minecraft/textures/"):
                        continue
                    mod_cfg_path = cfg_path.replace(
                        "assets/minecraft/textures/", f"assets/{modid}/textures/", 1
                    )
                    scan_paths.append(mod_cfg_path)

        for cfg_path in scan_paths:
            total += self._process_cfg_path(pack_dir, cfg_path, style)

        print(f"{pack_dir.name}: processed {total} textures into {self.processed_path}")

    def _load_style_info(self, pack_dir: Path) -> StyleInfo | None:
        """Load and parse style.json for a texture pack"""
        style_path = pack_dir / "style.json"
        if not style_path.exists():
            return None
        try:
            return StyleInfo(style_path)
        except Exception as e:
            print(f"[error] {pack_dir.name}: failed to load style.json - {e}")
            return None

    def _process_cfg_path(self, pack_dir: Path, cfg_path: str, style: StyleInfo) -> int:
        """Process a specific texture configuration path (e.g. "assets/minecraft/textures/block") in a texture pack"""
        kind = self.namer.define_kind(cfg_path)
        out_folder = ensure_dir_exists(self.processed_path)

        src = pack_dir / cfg_path

        images = list_images(src)
        if not images:
            return 0

        src_base = src if src.is_dir() else src.parent

        labels_str = ",".join(style.keywords)

        for src_img in images:
            base_name = self.namer.create_flat_name(kind, src_img, src_base)
            flat_name = f"{style.pack}-{base_name}"
            dst_img = out_folder / f"{flat_name}.png"

            img = process_image(src_img)
            img.save(dst_img)

            caption = self.caption_builder.build_caption(
                src_img.stem, kind, style.keywords
            )
            (out_folder / f"{flat_name}.txt").write_text(caption, encoding="utf-8")

            rel_path = str(dst_img.relative_to(self.processed_path)).replace("\\", "/")

            self.labels.append((rel_path, labels_str, style.pack, style.style, kind))

        return len(images)

    def _write_labels_csv(self) -> None:
        """Write the labels.csv file in the processed directory"""
        ensure_dir_exists(self.processed_path)
        labels_csv = self.processed_path / "labels.csv"

        with labels_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(["file", "labels", "pack", "style", "kind"])
            writer.writerows(self.labels)
