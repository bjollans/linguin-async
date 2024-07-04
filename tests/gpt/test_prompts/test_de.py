from tests.gpt.prompt_test_utils import assert_compound_does_not_exist, assert_compound_exists, assert_idiom_exists, assert_property
from util.gpt.prompts.word_splitting import get_gpt_word_splits


def test_german_sentence_splits_1():
    # This is just a vanilla test
    test_prompt = "Nach langem Überlegen tauchte sie in der Nachbarschaft auf"
    result_json = get_gpt_word_splits(test_prompt, "de")
    assert_property({"text": "Überlegen", "case": "dative",
                    "gender": "neuter"}, result_json)
    assert_compound_exists("auftauchen", ["tauchte", "auf"], result_json)
    assert_property({"text": "der", "case": "dative"}, result_json)
    _assert_no_wrong_cases(result_json)
    _assert_no_wrong_genders(result_json)

def test_german_sentence_splits_2():
    # This test is here, because "nachließ und ließ" was a compound
    test_prompt = "Sie verließ jedoch eilig den Ball um Mitternacht, bevor der Zauber nachließ, und ließ einen Schuh zurück."
    result_json = get_gpt_word_splits(test_prompt, "de")
    assert_compound_does_not_exist("nachließ und ließ", result_json)
    _assert_no_wrong_cases(result_json)
    _assert_no_wrong_genders(result_json)


def test_german_sentence_splits_3():
    # This test is here, because "ließ fallen" was hard to get into one compound
    test_prompt = "Zu ihrer Überraschung ließ ein wunderschöner Vogel ein prächtiges Kleid und gläserne Schuhe fallen, die sie zum Ball tragen sollte."
    result_json = get_gpt_word_splits(test_prompt, "de")

    assert_compound_exists("fallen lassen", ["ließ", "fallen"], result_json)
    assert_compound_does_not_exist("fallen tragen sollte", result_json)
    assert_compound_does_not_exist("zum Ball", result_json)
    _assert_no_wrong_cases(result_json)
    _assert_no_wrong_genders(result_json)


def test_german_sentence_splits_4():
    # This test is here, because "einmal" was not in the "sentence" part
    test_prompt = "Es war einmal ein liebes Mädchen namens Aschenputtel, das bei seiner grausamen Stiefmutter und zwei Stiefschwestern lebte."
    result_json = get_gpt_word_splits(test_prompt, "de")
    assert_property({"text": "Es"}, result_json)
    assert_property({"text": "war"}, result_json)
    assert_property({"text": "einmal"}, result_json)
    assert_property({"text": "ein"}, result_json)
    assert_property({"text": "liebes"}, result_json)
    assert_property({"text": "Mädchen"}, result_json)
    assert_property({"text": "namens"}, result_json)
    assert_property({"text": "Aschenputtel"}, result_json)
    assert_property({"text": "das"}, result_json)
    assert_property({"text": "bei"}, result_json)
    assert_property({"text": "seiner"}, result_json)
    assert_property({"text": "grausamen"}, result_json)
    assert_property({"text": "Stiefmutter"}, result_json)
    assert_property({"text": "und"}, result_json)
    assert_property({"text": "zwei"}, result_json)
    assert_property({"text": "Stiefschwestern"}, result_json)
    assert_property({"text": "lebte"}, result_json)
    _assert_no_wrong_cases(result_json)
    _assert_no_wrong_genders(result_json)


def test_german_sentence_splits_5():
    # This test is here, because "tailzunehmen" was split into 3 words and "hingehen" was split into 2 words
    test_prompt = "Aschenputtel wollte hingehen, aber ihre Stiefmutter stellte ihr unmögliche Aufgaben, um sie daran zu hindern, teilzunehmen."
    result_json = get_gpt_word_splits(test_prompt, "de")
    assert_property({"text":"Aschenputtel"}, result_json)
    assert_property({"text":"wollte"}, result_json)
    assert_property({"text":"hingehen"}, result_json)
    assert_property({"text":"aber"}, result_json)
    assert_property({"text":"ihre"}, result_json)
    assert_property({"text":"Stiefmutter"}, result_json)
    assert_property({"text":"stellte"}, result_json)
    assert_property({"text":"ihr"}, result_json)
    assert_property({"text":"unmögliche"}, result_json)
    assert_property({"text":"Aufgaben"}, result_json)
    assert_property({"text":"um"}, result_json)
    assert_property({"text":"sie"}, result_json)
    assert_property({"text":"daran"}, result_json)
    assert_property({"text":"zu"}, result_json)
    assert_property({"text":"hindern"}, result_json)
    assert_property({"text":"teilzunehmen"}, result_json)
    _assert_no_wrong_cases(result_json)
    _assert_no_wrong_genders(result_json)


def test_german_sentence_splits_6():
    # This test is here, because "hielt um ihre Hand an" was not one compound
    test_prompt = "Der Prinz erkannte, dass sie das Mädchen vom Ball war, und hielt um ihre Hand an."
    result_json = get_gpt_word_splits(test_prompt, "de")

    assert_compound_exists("um ihre Hand anhalten", ["hielt", "um", "ihre", "Hand", "an"], result_json)
    assert_compound_does_not_exist("anhalten", result_json)
    _assert_no_wrong_cases(result_json)
    _assert_no_wrong_genders(result_json)


def _assert_no_wrong_cases(result_json):
    cases = [x["case"] for x in result_json["sentence"] if "case" in x]
    for case in cases:
        assert case in ["nominative", "accusative", "dative", "genitive"]


def _assert_no_wrong_genders(result_json):
    genders = [x["gender"] for x in result_json["sentence"] if "gender" in x]
    for gender in genders:
        assert gender in ["masculine", "feminine", "neuter"]
