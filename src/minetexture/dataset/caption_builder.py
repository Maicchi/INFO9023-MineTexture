class CaptionBuilder:
    @staticmethod
    def build_caption(image_name: str, kind: str, style_keywords: list[str]) -> str:
        """Build a caption string with comma separations"""
        image_name = image_name.replace("_", " ").strip().lower()
        parts = [image_name, kind] + style_keywords

        seen: set[str] = set()
        unique_parts: list[str] = []

        for p in parts:
            p = p.strip().lower()
            if p and p not in seen:
                unique_parts.append(p)
                seen.add(p)

        return ", ".join(unique_parts)
