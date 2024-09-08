from googletrans import Translator

def translate_text(text, source_language, target_language):
    """
    Translate text from the source language to the target language.
    Returns: The translated text.
    """
    translator = Translator()
    
    # Translate the text
    translated = translator.translate(text, src=source_language, dest=target_language).text
    return translated

# Example usage
translated_text = translate_text("Hello, world!", 'en', 'es')
print("Translated Text:", translated_text)
