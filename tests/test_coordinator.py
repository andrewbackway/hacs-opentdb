from datetime import datetime, timedelta, timezone

from custom_components.opentdb.coordinator import QuizDataUpdateCoordinator


def test_prepare_question_shuffles_choices():
    question = {
        "correct_answer": "correct",
        "incorrect_answers": ["wrong 1", "wrong 2"],
    }

    prepared = QuizDataUpdateCoordinator._prepare_question(question)

    assert sorted(prepared["answers"]) == ["correct", "wrong 1", "wrong 2"]
    assert prepared["correct_answer"] == "correct"


def test_score_answer_awards_speed_and_streak_bonus():
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    player = {"presented_at": now.isoformat(), "streak": 0}

    speed_bonus, streak_bonus = QuizDataUpdateCoordinator._score_answer(player, True, now)

    assert speed_bonus == 100  # answered instantly -> full speed bonus
    assert player["streak"] == 1
    assert player["best_streak"] == 1
    assert streak_bonus == 25


def test_score_answer_speed_bonus_decays_to_zero():
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    player = {"presented_at": (now - timedelta(seconds=30)).isoformat(), "streak": 0}

    speed_bonus, _ = QuizDataUpdateCoordinator._score_answer(player, True, now)

    assert speed_bonus == 0  # slower than the speed window -> no bonus


def test_score_answer_wrong_resets_streak():
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    player = {"presented_at": now.isoformat(), "streak": 3}

    speed_bonus, streak_bonus = QuizDataUpdateCoordinator._score_answer(player, False, now)

    assert (speed_bonus, streak_bonus) == (0, 0)
    assert player["streak"] == 0


def test_update_play_streak_increments_on_consecutive_days():
    lifetime = {"last_played_date": "2026-01-01", "daily_play_streak": 2}

    QuizDataUpdateCoordinator._update_play_streak(lifetime, "2026-01-02")

    assert lifetime["daily_play_streak"] == 3
    assert lifetime["last_played_date"] == "2026-01-02"


def test_update_play_streak_resets_after_a_gap():
    lifetime = {"last_played_date": "2026-01-01", "daily_play_streak": 5}

    QuizDataUpdateCoordinator._update_play_streak(lifetime, "2026-01-03")

    assert lifetime["daily_play_streak"] == 1
