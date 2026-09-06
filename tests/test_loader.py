import os

import pytest

from custom_components.opentdb.loader import (
    QuestionFileEmptyError,
    QuestionFileInvalidError,
    _safe_path,
    normalise_question_set,
    parse_question_set,
    sample_questions,
)


def _set(questions):
    return {"topic": "Science", "difficulty": "easy", "questions": questions}


def test_normalise_maps_options_to_correct_and_incorrect():
    data = _set([{"question": "2+2?", "options": ["4", "3", "5", "6"], "answer": "4"}])

    result = normalise_question_set(data)

    assert len(result) == 1
    question = result[0]
    assert question["correct_answer"] == "4"
    assert sorted(question["incorrect_answers"]) == ["3", "5", "6"]
    assert question["category"] == "Science"
    assert question["difficulty"] == "easy"
    assert question["type"] == "multiple"


def test_normalise_two_options_is_boolean():
    data = _set([{"question": "Sky blue?", "options": ["Yes", "No"], "answer": "Yes"}])

    assert normalise_question_set(data)[0]["type"] == "boolean"


def test_normalise_skips_invalid_questions():
    data = _set(
        [
            {"question": "", "options": ["a", "b"], "answer": "a"},  # blank question
            {"question": "dup", "options": ["a", "a"], "answer": "a"},  # duplicate options
            {"question": "missing", "options": ["a", "b"], "answer": "c"},  # answer not present
            {"question": "one", "options": ["a"], "answer": "a"},  # too few options
            {"question": "ok", "options": ["a", "b", "c", "d"], "answer": "b"},
        ]
    )

    result = normalise_question_set(data)

    assert [question["question"] for question in result] == ["ok"]


def test_normalise_requires_questions():
    with pytest.raises(QuestionFileEmptyError):
        normalise_question_set({"questions": []})
    with pytest.raises(QuestionFileEmptyError):
        normalise_question_set({})


def test_normalise_all_invalid_raises_empty():
    with pytest.raises(QuestionFileEmptyError):
        normalise_question_set(_set([{"question": "x", "options": ["a"], "answer": "a"}]))


def test_parse_rejects_non_object():
    with pytest.raises(QuestionFileInvalidError):
        parse_question_set("[1, 2, 3]")
    with pytest.raises(QuestionFileInvalidError):
        parse_question_set("not json")


def test_sample_returns_requested_unique_subset():
    pool = [{"question": str(index)} for index in range(100)]

    picked = sample_questions(pool, 10)

    keys = {question["question"] for question in picked}
    assert len(picked) == 10
    assert len(keys) == 10
    assert keys.issubset({question["question"] for question in pool})


def test_sample_returns_whole_pool_when_amount_exceeds():
    pool = [{"question": str(index)} for index in range(5)]

    picked = sample_questions(pool, 10)

    assert len(picked) == 5
    assert {question["question"] for question in picked} == {q["question"] for q in pool}


def test_safe_path_rejects_traversal_and_non_json(tmp_path):
    base = str(tmp_path)
    for bad in ("../secrets.json", "sub/dir.json", "notjson.txt", ""):
        with pytest.raises(QuestionFileInvalidError):
            _safe_path(base, bad)


def test_safe_path_accepts_plain_json_name(tmp_path):
    base = str(tmp_path)

    resolved = _safe_path(base, "quiz.json")

    assert resolved == os.path.realpath(os.path.join(base, "quiz.json"))
