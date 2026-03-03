from __future__ import annotations

from pathlib import Path


class TextureNamer:
    @staticmethod
    def define_kind(texture_path: str) -> str:
        """Determine the 'kind' of a texture based on its path."""
        p = Path(texture_path)

        if p.name == "pack.png":
            return "root"

        parts = p.parts
        try:
            idx = parts.index("textures")
            kind = parts[idx + 1]
            if kind == "gui" and len(parts) > idx + 2:
                kind = f"{kind}_{parts[idx + 2]}"
            return kind.lower()
        except ValueError:
            return p.stem.lower()

    @staticmethod
    def create_flat_name(kind: str, image_path: Path, src_base: Path) -> str:
        """Create a flattened filename for a texture image."""
        if src_base.is_dir():
            rel = image_path.relative_to(src_base)
            rel_no_ext = rel.with_suffix("")
            rel_part = "_".join(rel_no_ext.parts)
            return f"{kind}_{rel_part}"
        return f"{kind}_{image_path.stem}"
