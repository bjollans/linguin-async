from util.gpt.prompts.word_splitting import remove_compounds_with_one_word, remove_words_not_in_sentence


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
    remove_compounds_with_one_word(test_json)
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
