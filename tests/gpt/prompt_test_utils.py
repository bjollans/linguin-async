

def assert_property(assert_obj, test_json):
    text = assert_obj.pop("text")
    assert len([x for x in test_json["sentence"] if x["text"] == text]) > 0
    for k, expected_value in assert_obj.items():
        actual_value = next(x[k]
                            for x in test_json["sentence"] if x["text"] == text)
        assert expected_value == actual_value

def assert_property_like(assert_obj, test_json):
    text = assert_obj.pop("text")
    assert len([x for x in test_json["sentence"] if x["text"] == text]) > 0
    for k, expected_value in assert_obj.items():
        actual_value = next(x[k]
                            for x in test_json["sentence"] if x["text"] == text)
        assert expected_value in actual_value


def assert_word_not_in_sentence(text, test_json):
    assert len([x for x in test_json["sentence"] if x["text"] == text]) == 0


def assert_compound_exists(compound_text, compound_parts, test_json):
    assert len([x["text"] for x in test_json["compounds"]
               if x["text"] == compound_text]) > 0
    # assert compound ids are the same across parts
    compound_part_jsons = [
        x for x in test_json["sentence"] if x["text"] in compound_parts]
    for i in range(0, len(compound_part_jsons) - 1):
        assert compound_part_jsons[i]["compound_id"] == compound_part_jsons[i + 1]["compound_id"]


def assert_compound_does_not_exist(compound_text, test_json):
    if "compounds" not in test_json:
        return
    assert len([x["text"] for x in test_json["compounds"]
               if x["text"] == compound_text]) == 0


def assert_idiom_exists(idiom_text, idiom_parts, test_json):
    assert len([x["text"]
               for x in test_json["idioms"] if x["text"] == idiom_text]) > 0
    # assert idiom ids are the same across parts
    idiom_part_jsons = [x for x in test_json["sentence"]
                        if x["text"] in idiom_parts]
    for i in range(0, len(idiom_part_jsons) - 1):
        assert idiom_part_jsons[i]["idiom_id"] == idiom_part_jsons[i + 1]["idiom_id"]
