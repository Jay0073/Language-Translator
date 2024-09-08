import speech_recognition as sr

def recognize_speech(language_code):
    """
    Recognize speech from the microphone in the given language.
    Returns: The recognized speech as text.
    """
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        print("Listening...")
        audio = recognizer.listen(source, timeout=5)  # Listens for 5 seconds

        # Convert speech to text
        text = recognizer.recognize_google(audio, language=language_code)
        return text

# Example usage
recognized_text = recognize_speech('en')
print("Recognized Text:", recognized_text)
