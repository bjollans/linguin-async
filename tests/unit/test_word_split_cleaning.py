from util.gpt.prompts.word_splitting import remove_compounds_that_are_same_as_one_word, remove_compounds_with_one_or_less_words_or_compounds, remove_non_existant_kanjis, remove_words_not_in_sentence


def test_remove_compounds_with_one_word_removes_single_word_compounds_and_idioms():
    test_json = {
        "sentence": [
            {"text": "", "compound_id": "1"},
            {"text": "", "compound_id": "1"},
            {"text": "", "compound_id": "2"},
            {"text": "", "compound_id": "3", "idiom_id": "1"},
            {"text": "", "idiom_id": "2"},
            {"text": "", "idiom_id": "3"},
            {"text": "", "idiom_id": "3"},
            {"text": "", "idiom_id": "4"},
            {"text": "", "idiom_id": "4", "compound_id": "4"},
            {"text": "", "compound_id": "5"},
            {"text": "", "compound_id": "5", "idiom_id": "5"},
            {"text": "", "compound_id": "6"},
            {"text": "", "compound_id": "6"},
            {"text": "", "compound_id": "6"},
            {"text": "", "compound_id": "6"},
            {"text": "", "idiom_id": "6"},
            {"text": "", "idiom_id": "6"},
            {"text": "", "idiom_id": "6"},
            {"text": "", "idiom_id": "6"},
        ],
        "compounds": [
            {"id": "1"},
            {"id": "2"},
            {"id": "3"},
            {"id": "4"},
            {"id": "5"},
            {"id": "6"},
            {"id": "7"},
        ],
        "idioms": [
            {"id": "1"},
            {"id": "2"},
            {"id": "3"},
            {"id": "4"},
            {"id": "5"},
            {"id": "6"},
            {"id": "7"},
        ]
    }
    expected_result_json = {
        "sentence": [
            {"text": "", "compound_id": "1"},
            {"text": "", "compound_id": "1"},
            {"text": ""},
            {"text": ""},
            {"text": ""},
            {"text": "", "idiom_id": "3"},
            {"text": "", "idiom_id": "3"},
            {"text": "", "idiom_id": "4"},
            {"text": "", "idiom_id": "4"},
            {"text": "", "compound_id": "5"},
            {"text": "", "compound_id": "5"},
            {"text": "", "compound_id": "6"},
            {"text": "", "compound_id": "6"},
            {"text": "", "compound_id": "6"},
            {"text": "", "compound_id": "6"},
            {"text": "", "idiom_id": "6"},
            {"text": "", "idiom_id": "6"},
            {"text": "", "idiom_id": "6"},
            {"text": "", "idiom_id": "6"},
        ],
        "compounds": [
            {"id": "1"},
            {"id": "5"},
            {"id": "6"},
        ],
        "idioms": [
            {"id": "3"},
            {"id": "4"},
            {"id": "6"},
        ]
    }
    remove_compounds_with_one_or_less_words_or_compounds(test_json)
    assert test_json == expected_result_json


def test_remove_words_not_in_sentence():
    test_text = "ある夜、ミコはキラキラと輝く光に目を奪われた。"
    test_json = {
        "sentence": [
            {"text": "ある"},
            {"text": "夜"},
            {"text": "ミコ"},
            {"text": "は"},
            {"text": "キラキラ"},
            {"text": "と"},
            {"text": "輝く"},
            {"text": "光"},
            {"text": "に"},
            {"text": "目"},
            {"text": "を"},
            {"text": "奪われた"},
            {"text": "奪う"},
        ]}
    expected_result_json = {
        "sentence": [
            {"text": "ある"},
            {"text": "夜"},
            {"text": "ミコ"},
            {"text": "は"},
            {"text": "キラキラ"},
            {"text": "と"},
            {"text": "輝く"},
            {"text": "光"},
            {"text": "に"},
            {"text": "目"},
            {"text": "を"},
            {"text": "奪われた"},
        ]}
    remove_words_not_in_sentence(test_text, test_json)
    assert test_json == expected_result_json


def test_remove_compounds_that_are_same_as_one_word_no_other_compound():
    test_json = {
        "sentence": [
            {"text": "を"},
            {"text": "奪われた", "compound_id": "1"},
        ],
        "compounds": [
            {"id": "1", "text": "奪われた"},
        ]}
    expected_result_json = {
        "sentence": [
            {"text": "を"},
            {"text": "奪われた"},
        ]}
    remove_compounds_that_are_same_as_one_word(test_json)
    assert expected_result_json == test_json


def test_remove_compounds_that_are_same_as_one_word():
    test_json = {
        "sentence": [
            {"text": "目", "compound_id": "1"},
            {"text": "を", "compound_id": "1"},
            {"text": "奪われた", "compound_id": "2"},
        ],
        "compounds": [
            {"id": "1", "text": "目 を"},
            {"id": "2", "text": "奪われた"},
        ]}
    expected_result_json = {
        "sentence": [
            {"text": "目", "compound_id": "1"},
            {"text": "を", "compound_id": "1"},
            {"text": "奪われた"},
        ],
        "compounds": [
            {"id": "1", "text": "目 を"},
        ]}
    remove_compounds_that_are_same_as_one_word(test_json)
    assert expected_result_json == test_json


def test_remove_non_existant_kanjis():
    text = "毎日、毛糸玉で遊び、日向で昼寝をしていた。"
    test_json = {
        "sentence": [
            {"text": "毎日", "kanjis": [{"text":"毎"}, {"text":"日"}]},
            {"text": "毛糸玉", "kanjis": [{"text":"毛"}, {"text":"糸"}, {"text":"玉"}, {"text":"奪"}]},
            {"text": "で"},
            {"text": "遊び", "kanjis": [{"text":"遊"}]},
            {"text": "日向", "kanjis": [{"text":"日"}, {"text":"向"}]},
            {"text": "で"},
            {"text": "昼寝", "kanjis": [{"text":"昼"}, {"text":"寝"}]},
            {"text": "を", "kanjis": []},
            {"text": "して", "kanjis": [{"text":"光"}, {"text":"輝"}]},
            {"text": "いた", "kanjis": [{"text":"夜"}]},
        ], }
    expected_result_json = {
        "sentence": [
            {"text": "毎日", "kanjis": [{"text":"毎"}, {"text":"日"}]},
            {"text": "毛糸玉", "kanjis": [{"text":"毛"}, {"text":"糸"}, {"text":"玉"}]},
            {"text": "で"},
            {"text": "遊び", "kanjis": [{"text":"遊"}]},
            {"text": "日向", "kanjis": [{"text":"日"}, {"text":"向"}]},
            {"text": "で"},
            {"text": "昼寝", "kanjis": [{"text":"昼"}, {"text":"寝"}]},
            {"text": "を"},
            {"text": "して"},
            {"text": "いた"},
        ], }
    remove_non_existant_kanjis(text, test_json)
    assert expected_result_json == test_json
