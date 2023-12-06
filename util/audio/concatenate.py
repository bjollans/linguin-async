from pydub.utils import mediainfo
from pydub import AudioSegment

def get_time_stamps(files):
    print(f"Getting time stamps for {files}")
    result = []
    current_start = 0

    for file in files:
        audio = AudioSegment.from_file(file, format="mp3")
        duration = len(audio)  # Duration in milliseconds
        current_end = current_start + duration / 1000  # Convert to seconds

        result.append({"start": current_start, "end": current_end})
        current_start = current_end

    return result


def concatenate_and_save_mp3(files, output_file):
    print(f"Concatenating {files} into {output_file}")
    concatenated_track = AudioSegment.empty()
    
    for file in files:
        audio = AudioSegment.from_file(file, format="mp3")
        concatenated_track += audio

    concatenated_track.export(output_file, format="mp3")


if __name__ == "__main__":
    mp3_files = ["util/audio/narakeet/0001.mp3", "util/audio/narakeet/0002.mp3", "util/audio/narakeet/0003.mp3", "util/audio/narakeet/0004.mp3", "util/audio/narakeet/0005.mp3", "util/audio/narakeet/0006.mp3", "util/audio/narakeet/0007.mp3", "util/audio/narakeet/0008.mp3", "util/audio/narakeet/0009.mp3", "util/audio/narakeet/0010.mp3", "util/audio/narakeet/0011.mp3", "util/audio/narakeet/0012.mp3", "util/audio/narakeet/0013.mp3", "util/audio/narakeet/0014.mp3", "util/audio/narakeet/0015.mp3", "util/audio/narakeet/0016.mp3", "util/audio/narakeet/0017.mp3", "util/audio/narakeet/0018.mp3", "util/audio/narakeet/0019.mp3", "util/audio/narakeet/0020.mp3"]
    output_file = "concatenated_audio.mp3"
    #concatenate_and_save_mp3(mp3_files, output_file)

    time_stamps = get_time_stamps(mp3_files)
    print(time_stamps)
