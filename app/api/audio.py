import logging

import moviepy.editor as mp
import ffmpeg


def extract_audio(file_path, file_name):
    audio_path = f"temp/{file_name}.mp3"
    clip = mp.VideoFileClip(file_path)

    if clip.audio is None:
        logging.debug("audio clip is None!")
        return None
    clip.audio.write_audiofile(audio_path)
    return audio_path


def combine_audio(converted_video_path, video_name, audio_path):
    logging.info(f"video_path: {converted_video_path}")

    merged_video_path = f"temp/final-{video_name}"
    input_video = ffmpeg.input(converted_video_path)
    added_audio = ffmpeg.input(audio_path)

    (
        ffmpeg
        .concat(input_video, added_audio, v=1, a=1)
        .output(merged_video_path)
        .run(overwrite_output=True, quiet=True)
    )
    return merged_video_path
