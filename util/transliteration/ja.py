import pykakasi

kks = pykakasi.kakasi()

def get_japanese_transliteration(text):
    result = kks.convert(text)
    return "".join([x["hira"] for x in result])