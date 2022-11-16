import logging

import moviepy.editor as mp


def extract_audio(file_path, file_name):
    audio_path = f"app/api/temp/{file_name}.mp3"
    clip = mp.VideoFileClip(file_path)
    if clip.audio is None:
        logging.debug("audio clip is None!")
        return None
    clip.audio.write_audiofile(audio_path)
    return audio_path


def combine_audio(video_path, audio_path):
    audio_clip = mp.AudioFileClip(audio_path)
    video_clip = mp.VideoFileClip(video_path)
    video_clip.set_audio(audio_clip)
