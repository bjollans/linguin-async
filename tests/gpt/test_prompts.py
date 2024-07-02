from util.gpt.prompts.word_splitting import get_gpt_word_splits


def test_hindi_sentence_splits_1():
    test_prompt = "किसान ने जितनी भी कोशिश की, वह गधे को बाहर नहीं निकाल पाया।"
    response_json = get_gpt_word_splits(test_prompt, "hi")

    _assert_property({"text": "गधे", "case": "oblique"}, response_json)
    _assert_property({"text": "किसान", "gender": "masculine"}, response_json)
    _assert_property({"text": "भी", "translation": "also"}, response_json)
    _assert_compound_exists("जितनी भी", ["जितनी", "भी"], response_json)
    _assert_compound_exists("निकाल पाया", ["निकाल", "पाया"], response_json)


def test_hindi_sentence_splits_2():
    test_prompt = "जैसे ही गांववालों ने कुएँ में मिट्टी डालना शुरू किया, गधे को समझ में आया कि क्या हो रहा है और वह जोर से बोला।"
    response_json = get_gpt_word_splits(test_prompt, "hi")

    _assert_property({"text": "गांववालों", "case": "oblique"}, response_json)
    _assert_property({"text": "गांववालों", "gender": "masculine"}, response_json)
    _assert_property({"text": "मिट्टी", "gender": "feminine"}, response_json)
    _assert_property({"text": "से", "translation": "from"}, response_json)
    _assert_compound_exists("जैसे ही", ["जैसे", "ही"], response_json)
    _assert_compound_exists("हो रहा है", ["हो", "रहा", "है"], response_json)
    _assert_compound_exists("जोर से", ["जोर", "से"], response_json)


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


def _assert_idiom_exists(idiom_text, idiom_parts, test_json):
    assert len([x["text"]
               for x in test_json["idioms"] if x["text"] == idiom_text]) > 0
    # assert idiom ids are the same across parts
    idiom_part_jsons = [x for x in test_json["sentence"]
                        if x["text"] in idiom_parts]
    for i in range(0, len(idiom_part_jsons) - 1):
        assert idiom_part_jsons[i]["idiom_id"] == idiom_part_jsons[i + 1]["idiom_id"]
