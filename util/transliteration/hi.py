from collections import namedtuple

from devatrans import DevaTrans


def split_syllables_transliterated(word):
    vowels = {'a', 'e', 'i', 'o', 'u', "ā", "ū", "ī", "़"} # Add nukta (़), because DevaTrans messes it up
    syllables = []
    current_syllable = ''
    for i, char in enumerate(word):
        has_any_vowel = any([vowel in current_syllable for vowel in vowels])
        if char not in vowels and \
                current_syllable != '' and \
                has_any_vowel:
            syllables.append(current_syllable)
            current_syllable = ''
        current_syllable += char
    if current_syllable != '':
        syllables.append(current_syllable)
    return syllables


def ends_with_matra(word):
    if len(word) < 1:
        return False
    matra_start = 0x093E
    matra_end = 0x094C
    last_char = word[-1]
    return matra_start <= ord(last_char) <= matra_end



def apply_a_dropping_rules(word, transliteration):
    # Remove 'a' from the end of the word
    removed_unnecessary_a_at_end_of_words = transliteration[:-
                                                            1] if transliteration.endswith("a") else transliteration
    syllables = split_syllables_transliterated(
        removed_unnecessary_a_at_end_of_words)
    # Remove 'a' from the second letter in a 3-letter-word that ends in a Matra
    if ends_with_matra(word) and len(syllables) == 3 and syllables[1][-1] == 'a':
        syllables[1] = syllables[1][:-1]
    # Remove 'a' from the second letter in a 4-letter-word that does NOT end in a Matra
    if (not ends_with_matra(word)) and len(syllables) == 4 and syllables[1][-1] == 'a':
        syllables[1] = syllables[1][:-1]
    # Remove 'a' from the third letter in a 4-letter-word that ends in a Matra
    if ends_with_matra(word) and len(syllables) == 4 and syllables[2][-1] == 'a':
        syllables[2] = syllables[2][:-1]
    return "".join(syllables)


def fix_nukta(transliteration):
    nukta = "़"
    syllables = split_syllables_transliterated(transliteration)
    for i, syllable in enumerate(syllables):
        if nukta in syllable:
            if syllable[0] == "ḍ":
                syllables[i] = syllables[i].replace(nukta,"").replace("ḍ","ṛ")
            else:
                syllables[i] = syllables[i].replace(nukta,"")
    return "".join(syllables)


def replace_wrong_latin_letters(transliteration):
    return transliteration\
        .replace("ch", "------")\
        .replace("c", "ch")\
        .replace("------", "chh")


# test cases
# छिड़कते = chhiṛakte
# लड़का = laṛkā

def get_indic_transliteration_for_word(word):
    dt = DevaTrans()
    deva_transliteration = dt.transliterate(
        input_type="sen", to_convention="iast", sentence=word)
    without_wrong_nukta = fix_nukta(deva_transliteration)
    with_dropped_as = apply_a_dropping_rules(word, without_wrong_nukta)
    with_replaced_letters = replace_wrong_latin_letters(with_dropped_as)
    return with_replaced_letters


def get_indic_transliteration(text):
    return " ".join([get_indic_transliteration_for_word(word) for word in text.split(" ")])


if __name__ == "__main__":
    split_syllables_transliterated("kakalu")