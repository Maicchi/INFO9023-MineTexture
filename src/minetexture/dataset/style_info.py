from __future__ import annotations

import re
from pathlib import Path
from typing import Any, List
import json

class StyleInfo:
    """
    Parse style.json files in texture packs.
    """

    def __init__(self, style_path: Path) -> None:
        """
        Initialize the StyleInfo object

        Parameters: 
            - style_path: Path to the style.json file
        """
        self.style_path = style_path
        self.pack, self.style, self.keywords, self.texture_path = self._parse_style_file()

    def _parse_style_file(self) -> tuple[str, str, List[str], str | None]:
        """ 
        Parse style.json file.

        Return:
            - pack: the name of the texture pack
            - style: a normalized name for the style
            - keywords: a list of lowercase keywords describing the style
            - texture_path: the path to the texture images (for mods)
        """
        try:
            data = json.loads(self.style_path.read_text(encoding="utf-8", errors="strict"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in style file {self.style_path}: {e}") from e

        if not isinstance(data, dict):
            raise ValueError(f"style file must be a JSON object: {self.style_path}")

        pack = self._as_str(data.get("texture_pack_name"))
        if not pack:
            raise ValueError(f"Missing or empty 'texture_pack_name' in style file {self.style_path}")
        pack_slug = self._normalize(pack)

        style_value = self._as_str(data.get("style"))
        if not style_value:
            raise ValueError(f"Missing or empty 'style' in style file {self.style_path}")

        style_slug = self._normalize(style_value)

        keywords = self._parse_keywords_from_rest(data.get("keywords"))

        # Add style words into keywords too
        style_words = [w for w in re.split(r"\s+", style_value.lower()) if w]

        merged: List[str] = []
        for k in keywords + style_words:
            k2 = k.strip().lower()
            if k2 and k2 not in merged:
                merged.append(k2)

        texture_path = self._as_str(data.get("texture_path"))

        return pack_slug, style_slug, merged, texture_path

    @staticmethod
    def _as_str(value) -> str | None:
        """
        Convert a value to string
        """
        if value is None:
            return None
        value = str(value).strip()
        return value

    @staticmethod
    def _parse_keywords_from_rest(text: Any) -> List[str]:
        """
        Extract keywords
        """

        if text is None:
            return []

        if isinstance(text, list):
            out: List[str] = []
            for item in text:
                if item is None:
                    continue
                s = str(item).strip()
                if s:
                    out.append(s)
            return out

        if isinstance(text, str):
            s = text.strip()
            if not s:
                return []
            if "," in s:
                return [k.strip() for k in s.split(",") if k.strip()]
            return [k.strip() for k in s.split() if k.strip()]

        s = str(text).strip()
        if not s:
            return []
        if "," in s:
            return [k.strip() for k in s.split(",") if k.strip()]
        return [k.strip() for k in s.split() if k.strip()]

    @staticmethod
    def _normalize(s: str) -> str:
        """
        Convert a string into a normalized slug form 
            - lowercase
            - non-alphanumeric replaced with underscores
        """
        s = s.strip().lower()
        s = re.sub(r"[^a-z0-9]+", "_", s)
        return s.strip("_")