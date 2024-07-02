from util.gpt.prompts.word_splitting import get_gpt_word_splits


def test_hindi_sentence_splits_1():
    test_prompt = "किसान ने जितनी भी कोशिश की, वह गधे को बाहर नहीं निकाल पाया।"
    result_json = get_gpt_word_splits(test_prompt, "hi")

    _assert_property({"text": "गधे", "case": "oblique"}, result_json)
    _assert_property({"text": "किसान", "gender": "masculine"}, result_json)
    _assert_property({"text": "भी", "translation": "also"}, result_json)
    _assert_compound_exists("जितनी भी", ["जितनी", "भी"], result_json)
    _assert_compound_exists("निकाल पाया", ["निकाल", "पाया"], result_json)


def test_hindi_sentence_splits_2():
    test_prompt = "जैसे ही गांववालों ने कुएँ में मिट्टी डालना शुरू किया, गधे को समझ में आया कि क्या हो रहा है और वह जोर से बोला।"
    result_json = get_gpt_word_splits(test_prompt, "hi")

    _assert_property({"text": "गांववालों", "case": "oblique"}, result_json)
    _assert_property({"text": "गांववालों", "gender": "masculine"}, result_json)
    _assert_property({"text": "मिट्टी", "gender": "feminine"}, result_json)
    _assert_property({"text": "से", "translation": "from"}, result_json)
    _assert_compound_exists("जैसे ही", ["जैसे", "ही"], result_json)
    _assert_compound_exists("हो रहा है", ["हो", "रहा", "है"], result_json)
    _assert_compound_exists("जोर से", ["जोर", "से"], result_json)

def test_japanese_sentence_splits_1():
    test_prompt = "間近で見ると、それはもっと美しくなかった。"
    result_json = get_gpt_word_splits(test_prompt, "ja")
    _assert_property({"text": "は", "translation": "topic marker"}, result_json)
    _assert_compound_exists("美しくなかった", ["美しく", "なかった"], result_json)
    _assert_compound_does_not_exist("見ると", result_json)
    _assert_property({"text": "見る", "kanjis": ["見"]}, result_json)
    _assert_property({"text": "間近", "kanjis": ["間", "近"]}, result_json)
    _assert_kanji("間", "カン", "あいだ", "interval", result_json)
    _assert_kanji("見", "ケン", "み", "see", result_json)


def test_japanese_sentence_splits_2():
    test_prompt = "ある夜、ミコはキラキラと輝く光に目を奪われた。"
    result_json = get_gpt_word_splits(test_prompt, "ja")
    _assert_compound_does_not_exist("奪われた", result_json)

def test_german_sentence_splits_1():
    test_prompt = "Nach langem Überlegen tauchte sie in der Nachbarschaft auf"
    result_json = get_gpt_word_splits(test_prompt, "de")
    _assert_property({"text": "Überlegen", "case": "dative", "gender": "neuter"}, result_json)
    _assert_compound_exists("tauchte auf", ["tauchte", "auf"], result_json)
    _assert_property({"text": "der", "case": "dative"}, result_json)

def test_german_sentence_splits_2():
    test_prompt = "Er sagte seinem Sohn, er solle nicht um den heißen Brei herum reden."
    result_json = get_gpt_word_splits(test_prompt, "de")
    _assert_idiom_exists("um den heißen Brei herum reden", ["um", "den", "heißen", "Brei", "herum", "reden"], result_json)
    _assert_compound_does_not_exist("sagte solle", result_json)

def test_chinese_sentence_splits_1():
    test_prompt = "他的演讲已经很精彩了，最后那句名言更是画龙点睛。"
    result_json = get_gpt_word_splits(test_prompt, "zh")
    _assert_property({"text": "画龙点睛", "translation": "finishing touch"}, result_json)
    _assert_hanzi("已","already", result_json)
    _assert_not_hanzi("他", result_json)

def _assert_property(assert_obj, test_json):
    text = assert_obj.pop("text")
    for k, expected_value in assert_obj.items():
        actual_value = next(x[k]
                            for x in test_json["sentence"] if x["text"] == text)
        assert expected_value == actual_value


def _assert_compound_exists(compound_text, compound_parts, test_json):
    assert len([x["text"] for x in test_json["compounds"]
               if x["text"] == compound_text]) > 0
    # assert compound ids are the same across parts
    compound_part_jsons = [
        x for x in test_json["sentence"] if x["text"] in compound_parts]
    for i in range(0, len(compound_part_jsons) - 1):
        assert compound_part_jsons[i]["compound_id"] == compound_part_jsons[i + 1]["compound_id"]


def _assert_compound_does_not_exist(compound_text, test_json):
    if "compounds" not in test_json: 
        return
    assert len([x["text"] for x in test_json["compounds"]
               if x["text"] == compound_text]) == 0


def _assert_idiom_exists(idiom_text, idiom_parts, test_json):
    assert len([x["text"]
               for x in test_json["idioms"] if x["text"] == idiom_text]) > 0
    # assert idiom ids are the same across parts
    idiom_part_jsons = [x for x in test_json["sentence"]
                        if x["text"] in idiom_parts]
    for i in range(0, len(idiom_part_jsons) - 1):
        assert idiom_part_jsons[i]["idiom_id"] == idiom_part_jsons[i + 1]["idiom_id"]


def _assert_kanji(kanji_text, on, kun, meaning, test_json):
    kanji = next(x for x in test_json["kanjis"] if x["text"] == kanji_text)
    assert on in kanji["on"]
    assert kun in kanji["kun"]
    assert meaning in kanji["meaning"]

def _assert_hanzi(hanzi_text, meaning, test_json):
    hanzi = next(x for x in test_json["hanzis"] if x["text"] == hanzi_text)
    assert meaning in hanzi["meaning"]

def _assert_not_hanzi(hanzi_text, test_json):
    assert len([x for x in test_json["hanzis"] if x["text"] == hanzi_text]) == 0
