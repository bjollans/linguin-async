from tests.gpt.prompt_test_utils import assert_compound_does_not_exist, assert_compound_exists, assert_idiom_exists, assert_property
from util.gpt.prompts.word_splitting import get_gpt_word_splits


def test_german_sentence_splits_1():
    test_prompt = "Nach langem Überlegen tauchte sie in der Nachbarschaft auf"
    result_json = get_gpt_word_splits(test_prompt, "de")
    assert_property({"text": "Überlegen", "case": "dative", "gender": "neuter"}, result_json)
    assert_compound_exists("tauchte auf", ["tauchte", "auf"], result_json)
    assert_property({"text": "der", "case": "dative"}, result_json)

def test_german_sentence_splits_2():
    test_prompt = "Er sagte seinem Sohn, er solle nicht um den heißen Brei herum reden."
    result_json = get_gpt_word_splits(test_prompt, "de")
    assert_idiom_exists("um den heißen Brei herum reden", ["um", "den", "heißen", "Brei", "herum", "reden"], result_json)
    assert_compound_does_not_exist("sagte solle", result_json)