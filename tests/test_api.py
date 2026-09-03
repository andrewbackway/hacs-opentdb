from custom_components.opentdb.api import OpenTDBClient


def test_decode_question_html_entities():
    question = OpenTDBClient._decode_question(
        {
            "category": "Science &amp; Nature",
            "type": "multiple",
            "difficulty": "easy",
            "question": "Who said &quot;hello&quot;?",
            "correct_answer": "A &amp; B",
            "incorrect_answers": ["C", "D", "E"],
        }
    )

    assert question["category"] == "Science & Nature"
    assert question["question"] == 'Who said "hello"?'
    assert question["correct_answer"] == "A & B"
