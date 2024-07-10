from tests.gpt.prompt_test_utils import assert_compound_does_not_exist, assert_compound_exists, assert_property, assert_word_not_in_sentence
from util.gpt.prompts.word_splitting import get_gpt_word_splits


def test_japanese_sentence_splits_1():
    test_prompt = "間近で見ると、それはもっと導いてくれた。"
    result_json = get_gpt_word_splits(test_prompt, "ja")
    assert_property({"text": "は", "translation": "topic marker"}, result_json)
    assert_compound_exists("導いてくれた", ["導いて", "くれた"], result_json)
    assert_compound_does_not_exist("見ると", result_json)
    assert_kanji("間近","間", "カン", "あいだ", "interval", result_json)
    assert_kanji("見る","見", "ケン", "み", "see", result_json)


def test_japanese_sentence_splits_2():
    test_prompt = "ある夜、ミコはキラキラと輝く光に目を奪われた。"
    result_json = get_gpt_word_splits(test_prompt, "ja")
    assert_compound_does_not_exist("奪われた", result_json)
    assert_property({"text": "奪われた"}, result_json)
    assert_word_not_in_sentence("た", result_json)
    assert_word_not_in_sentence("れ", result_json)
    assert_word_not_in_sentence("れた", result_json)
    assert_word_not_in_sentence("われた", result_json)
    assert_no_kanjis("ある", result_json)


def test_japanese_sentence_splits_3():
    test_prompt = "ある夜、ミコはよく寝ていた。"
    result_json = get_gpt_word_splits(test_prompt, "ja")
    assert_no_kanjis("ある", result_json)
    assert_no_kanjis("よく", result_json)
    assert_no_kanjis("いた", result_json)


def test_japanese_sentence_splits_4():
    test_prompt = "毎日、毛糸玉で遊び、日向で昼寝をしていた。"
    result_json = get_gpt_word_splits(test_prompt, "ja")
    assert_kanji("遊び","遊","ユ","あそ","play", result_json)


def test_japanese_sentence_splits_5():
    # Test because 飛び跳ねて was split into 飛び跳ね and て
    test_prompt = "遊び好きな子猫が飛び跳ねて糸を捕まえようとする。"
    result_json = get_gpt_word_splits(test_prompt, "ja")
    assert_property({"text": "飛び跳ねて"}, result_json)
    assert_word_not_in_sentence("て", result_json)
    assert_compound_does_not_exist("飛び跳ねて", result_json)


def test_japanese_sentence_splits_6():
    # Test because 抱きしめた was split into 抱きしめ and た
    test_prompt = "ミアは大喜びでタマを抱きしめた。"
    result_json = get_gpt_word_splits(test_prompt, "ja")
    assert_property({"text": "抱きしめた"}, result_json)
    assert_word_not_in_sentence("抱きしめ", result_json)
    assert_word_not_in_sentence("た", result_json)


def test_japanese_sentence_splits_7():
    # Test because 近づいてきて contained づ as Kanji
    test_prompt = "その翌日、浦島太郎が岸辺に座っていると、巨大な亀が近づいてきて、その親切に感謝した。"
    result_json = get_gpt_word_splits(test_prompt, "ja")
    assert_not_a_kanji("づ", result_json)



def assert_kanji(text, kanji_text, on, kun, meaning, test_json):
    kanji_list = next(x["kanjis"] for x in test_json["sentence"] if x["text"] == text)
    kanji = next(x for x in kanji_list if x["text"] == kanji_text)
    assert on in kanji["on"]
    assert kun in kanji["kun"]
    assert meaning in kanji["meaning"]


def assert_no_kanjis(text, test_json):
    assert len([x for x in test_json["sentence"] if x["text"] == text and "kanjis" in x]) == 0


def assert_not_a_kanji(text, test_json):
    for translation in test_json["sentence"]:
        if "kanjis" in translation:
            for kanji in translation["kanjis"]:
                assert kanji["text"] != text