import unicodedata


def normalize_text(stylized_text: str) -> str:
    return unicodedata.normalize("NFKC", stylized_text)
