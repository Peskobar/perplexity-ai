from typing import List
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.audio.io.AudioFileClip import AudioFileClip


def create_video(image_paths: List[str], audio_path: str | None = None, output: str = "output.mp4", fps: int = 24) -> str:
    """Create a video from image sequence and optional audio."""
    clip = ImageSequenceClip(image_paths, fps=fps)
    if audio_path:
        clip = clip.set_audio(AudioFileClip(audio_path))
    clip.write_videofile(output, codec="libx264", audio_codec="aac")
    return output
