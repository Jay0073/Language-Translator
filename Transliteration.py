from unidecode import unidecode

def transliterate_text(text):
    """
    Transliterate text to ASCII.
    Returns: The transliterated text.
    """
    return unidecode(text)

# Example usage
transliterated_text = transliterate_text("வணக்கம் உலகம்")
print("Transliterated Text:", transliterated_text)
