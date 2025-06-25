import pyttsx3


def text_to_speech(text: str, output_path: str) -> str:
    """Convert text to speech and save as an audio file."""
    engine = pyttsx3.init()
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    return output_path
