from tests.gpt.prompt_test_utils import assert_compound_exists, assert_property
from util.gpt.prompts.word_splitting import get_gpt_word_splits


def test_hindi_sentence_splits_1():
    test_prompt = "किसान ने जितनी भी कोशिश की, वह गधे को बाहर नहीं निकाल पाया।"
    result_json = get_gpt_word_splits(test_prompt, "hi")

    assert_property({"text": "गधे", "case": "oblique"}, result_json)
    assert_property({"text": "किसान", "gender": "masculine"}, result_json)
    assert_property({"text": "भी", "translation": "also"}, result_json)
    assert_compound_exists("जितनी भी", ["जितनी", "भी"], result_json)
    assert_compound_exists("निकाल पाया", ["निकाल", "पाया"], result_json)


def test_hindi_sentence_splits_2():
    test_prompt = "जैसे ही गांववालों ने कुएँ में मिट्टी डालना शुरू किया, गधे को समझ में आया कि क्या हो रहा है और वह जोर से बोला।"
    result_json = get_gpt_word_splits(test_prompt, "hi")

    assert_property({"text": "गांववालों", "case": "oblique"}, result_json)
    assert_property({"text": "गांववालों", "gender": "masculine"}, result_json)
    assert_property({"text": "मिट्टी", "gender": "feminine"}, result_json)
    assert_property({"text": "से", "translation": "from"}, result_json)
    assert_compound_exists("जैसे ही", ["जैसे", "ही"], result_json)
    assert_compound_exists("हो रहा है", ["हो", "रहा", "है"], result_json)
    assert_compound_exists("जोर से", ["जोर", "से"], result_json)