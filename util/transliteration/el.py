from transliterate import translit

def get_greek_transliteration(text):
    return translit(text, 'el', reversed=True)