from util.audio.concatenate import concatenate_and_save_mp3, get_time_stamps
from util.audio.generate import generate_audio_for_text


def text_to_audio_with_sentence_timestamps(text, lang, output_file):
    generated_file_prefix = "narakeet"
    generated_files = generate_audio_for_text(text, lang, generated_file_prefix)
    concatenate_and_save_mp3(generated_files, output_file)
    sentence_timestamps = get_time_stamps(generated_files)
    return sentence_timestamps