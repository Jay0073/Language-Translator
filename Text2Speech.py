from gtts import gTTS
import os

def convert_text_to_speech(text, language_code):
    """
    Convert the provided text to speech and save it as an audio file.

    Args:
        text (str): The text to convert to speech.
        language_code (str): The language code for the speech (e.g., 'en' for English).
    """
    tts = gTTS(text=text, lang=language_code)

    tts.save("speech.mp3")
    os.system('start speech.mp3') 

# Example usage
convert_text_to_speech("Hello, world!", "en")
