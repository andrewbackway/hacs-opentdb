from custom_components.opentdb.coordinator import QuizDataUpdateCoordinator


def test_prepare_question_shuffles_choices():
    question = {
        "correct_answer": "correct",
        "incorrect_answers": ["wrong 1", "wrong 2"],
    }

    prepared = QuizDataUpdateCoordinator._prepare_question(question)

    assert sorted(prepared["answers"]) == ["correct", "wrong 1", "wrong 2"]
    assert prepared["correct_answer"] == "correct"
