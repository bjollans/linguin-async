from dragonmapper import hanzi

def get_chinese_transliteration(text):
    return hanzi.to_pinyin(text)