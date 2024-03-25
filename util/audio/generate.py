import requests
import os

lang_to_voice = {
    "hi": "preeti",
    "ja": "tomoka",
    "de": "martina",
    "el": "eleni",
    "zh": "meilan",
}

def generate_audio_for_text(text, lang, output_file_prefix):
    print(f"Generating audio for {text} in {lang} and with prefix {output_file_prefix}")
    sentences = [s.strip() for s in text.split("\n") if len(s.strip()) > 0]
    output_files = []
    for i, sentence in enumerate(sentences):
        output_file = f"/tmp/{output_file_prefix}_{i}.mp3"
        output_files.append(output_file)
        generate_audio_for_sentence(sentence, lang, output_file, speed="normal")
    return output_files

def generate_audio_for_sentence(text, lang, output_file, speed="normal"):
    print(f"Generating audio for {text} in {lang} and saving to {output_file}")
    if lang not in lang_to_voice:
        raise Exception(f"Language {lang} not supported")
    
    voice_speed = speed
    file_format = "mp3"
    apikey = os.environ["NARAKEET_API_KEY"]
    voice = lang_to_voice[lang]
    url = f'https://api.narakeet.com/text-to-speech/{file_format}' + \
        f'?voice={voice}&voice-speed={voice_speed}'


    options = {
        'headers': {
            'Accept': 'application/octet-stream',
            'Content-Type': 'text/plain',
            'x-api-key': apikey,
        },
        'data': text.encode('utf8')
    }

    with open(output_file, 'wb') as f:
        f.write(requests.post(url, **options).content)

if __name__ == "__main__":
    text = """
एक समय की बात है, भारत के एक घने जंगल में एक चतुर सियार रहता था।
वह हमेशा भूखा रहता था और लगातार भोजन की तलाश में रहता था।
एक दिन, भोजन की तलाश करते हुए, वह भटक कर पास के एक गाँव में पहुँच गया।


जब वह बाहर आया तो सिर से पूंछ तक बिल्कुल नीला था।
उसने पास के एक तालाब में अपने प्रतिबिंब को देखा और अपना नया रूप देखकर आश्चर्यचकित रह गया।
"""
    lang = "hi"
    output_file_prefix = "test"
    generate_audio_for_text(text, lang, output_file_prefix)