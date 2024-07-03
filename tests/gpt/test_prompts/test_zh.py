from tests.gpt.prompt_test_utils import assert_property
from util.gpt.prompts.word_splitting import get_gpt_word_splits


def test_chinese_sentence_splits_1():
    test_prompt = "他的演讲已经很精彩了，最后那句名言更是画龙点睛。"
    result_json = get_gpt_word_splits(test_prompt, "zh")
    assert_property({"text": "画龙点睛", "translation": "finishing touch"}, result_json)
    assert_hanzi("已经","已","already", result_json)
    assert_no_hanzis("他", result_json)



def assert_hanzi(text, hanzi_text, meaning, test_json):
    hanzi_list = next(x["hanzis"] for x in test_json["sentence"] if x["text"] == text)
    hanzi = next(x for x in hanzi_list if x["text"] == hanzi_text)
    assert meaning in hanzi["meaning"]

def assert_no_hanzis(text, test_json):
    assert len([x for x in test_json["sentence"] if x["text"] == text and "hanzis" in x]) == 0