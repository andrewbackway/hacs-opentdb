from __future__ import annotations

import logging
import secrets
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import OpenTDBClient, OpenTDBError, OpenTDBTokenError
from .const import (
    CONF_AMOUNT,
    CONF_CATEGORY,
    CONF_DIFFICULTY,
    CONF_TYPE,
    DOMAIN,
    POINTS_BASE,
    SPEED_BONUS_MAX,
    SPEED_WINDOW_SECONDS,
    STORAGE_VERSION,
    STREAK_BONUS_CAP,
    STREAK_BONUS_STEP,
)

_LOGGER = logging.getLogger(__name__)


class QuizDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Own one quiz set and the per-user progress for that set."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, api: OpenTDBClient) -> None:
        super().__init__(hass, _LOGGER, name=f"{DOMAIN}_{entry.entry_id}", config_entry=entry)
        self.entry = entry
        self.api = api
        self.store = Store(hass, STORAGE_VERSION, f"{DOMAIN}_{entry.entry_id}")
        self._stored: dict[str, Any] = {
            "version": STORAGE_VERSION,
            "players": {},
            "lifetime_stats": {},
        }
        self._active_user: str | None = None

    async def async_load_stored(self) -> None:
        stored = await self.store.async_load()
        if isinstance(stored, dict):
            self._stored.update(stored)
        self._stored.setdefault("players", {})
        self._stored.setdefault("lifetime_stats", {})

    def set_active_user(self, user_id: str) -> None:
        self._active_user = user_id
        self.async_set_updated_data(self._build_view(user_id))

    def set_player_name(self, user_id: str, name: str) -> None:
        """Remember a friendly name so the leaderboard can show it."""
        if name:
            self._stored.setdefault("player_names", {})[user_id] = name

    @property
    def has_questions(self) -> bool:
        return bool(self._stored.get("questions"))

    async def async_start_quiz(self, user_id: str, force_new: bool = False) -> None:
        self.set_active_user(user_id)
        if force_new or not self._stored.get("questions"):
            await self._load_new_set()
        self._stored.setdefault("players", {})[user_id] = self._new_player(user_id)
        stats = self._stored["players"][user_id]["stats"]
        stats["quizzes_started"] = stats.get("quizzes_started", 0) + 1
        self._stored.setdefault("lifetime_stats", {})[user_id] = stats.copy()
        await self._save()
        self.async_set_updated_data(self._build_view(user_id))

    async def async_daily_refresh(self) -> None:
        """Fetch one shared question set for the day (best-effort)."""
        try:
            await self._load_new_set()
        except (UpdateFailed, OpenTDBError) as err:
            _LOGGER.warning("Daily OpenTDB refresh failed: %s", err)
            return
        await self._save()
        self.async_set_updated_data(self._build_view(self._active_user))

    async def _load_new_set(self) -> None:
        settings = self.entry.data | self.entry.options
        questions = await self._fetch_questions(settings)
        if not questions:
            raise UpdateFailed("OpenTDB returned no questions")
        self._stored.update(
            {
                "set_id": secrets.token_hex(8),
                "questions": [self._prepare_question(question) for question in questions],
                "created_at": dt_util.utcnow().isoformat(),
                "players": {},
            }
        )

    async def async_answer_question(self, user_id: str, question_index: int, answer: str) -> bool:
        self.set_active_user(user_id)
        questions = self._stored.get("questions", [])
        player = self._player(user_id)
        if player.get("index", 0) != question_index:
            raise ValueError("The question is no longer current")
        if player.get("feedback") is not None:
            raise ValueError("This question has already been answered")
        if not questions or question_index >= len(questions):
            raise ValueError("There is no active question")

        question = questions[question_index]
        correct = secrets.compare_digest(answer, question["correct_answer"])
        now = dt_util.utcnow()
        speed_bonus, streak_bonus = self._score_answer(player, correct, now)
        awarded = (POINTS_BASE + speed_bonus + streak_bonus) if correct else 0
        player["points"] = player.get("points", 0) + awarded
        player["feedback"] = {
            "correct": correct,
            "answer": answer,
            "correct_answer": question["correct_answer"],
            "awarded_points": awarded,
            "speed_bonus": speed_bonus,
            "streak_bonus": streak_bonus,
        }
        player["answered"] = player.get("answered", 0) + 1
        player["correct"] = player.get("correct", 0) + int(correct)
        lifetime = player.setdefault("stats", {})
        lifetime["questions"] = lifetime.get("questions", 0) + 1
        lifetime["correct"] = lifetime.get("correct", 0) + int(correct)
        lifetime["percentage"] = round(lifetime["correct"] / lifetime["questions"] * 100, 1)
        lifetime["total_points"] = lifetime.get("total_points", 0) + awarded
        lifetime["best_streak"] = max(lifetime.get("best_streak", 0), player.get("best_streak", 0))
        today = now.date().isoformat()
        week = now.date().isocalendar()
        week_key = f"{week.year}-W{week.week:02d}"
        day_bucket = lifetime.setdefault("daily", {}).setdefault(
            today, {"questions": 0, "correct": 0, "points": 0}
        )
        day_bucket["questions"] += 1
        day_bucket["correct"] += int(correct)
        day_bucket["points"] = day_bucket.get("points", 0) + awarded
        lifetime.setdefault("weekly", {}).setdefault(week_key, {"questions": 0, "correct": 0})
        lifetime["weekly"][week_key]["questions"] += 1
        lifetime["weekly"][week_key]["correct"] += int(correct)
        self._update_play_streak(lifetime, today)
        self._stored.setdefault("lifetime_stats", {})[user_id] = lifetime.copy()
        player.setdefault("answers", {})[str(question_index)] = {
            "correct": correct,
            "answered_at": now.isoformat(),
        }
        await self._save()
        self.async_set_updated_data(self._build_view(user_id))
        return correct

    async def async_next_question(self, user_id: str) -> None:
        self.set_active_user(user_id)
        player = self._player(user_id)
        if player.get("feedback") is None:
            raise ValueError("Answer the current question first")
        player["index"] = player.get("index", 0) + 1
        player["feedback"] = None
        if player["index"] >= len(self._stored.get("questions", [])):
            player["complete"] = True
            player["completed_at"] = dt_util.utcnow().isoformat()
            self._record_completion(player)
        else:
            player["presented_at"] = dt_util.utcnow().isoformat()
        await self._save()
        self.async_set_updated_data(self._build_view(user_id))

    async def async_reset_quiz(self, user_id: str) -> None:
        self.set_active_user(user_id)
        self._player(user_id).clear()
        await self._save()
        self.async_set_updated_data(self._build_view(user_id))

    async def async_reset_quiz_for_all(self) -> None:
        self._stored["questions"] = []
        self._stored["players"] = {}
        await self._save()
        self.async_set_updated_data(self._build_view(self._active_user))

    async def async_refresh(self) -> None:
        self.async_set_updated_data(self._build_view(self._active_user))

    async def _async_update_data(self) -> dict[str, Any]:
        return self._build_view(self._active_user)

    async def _fetch_questions(self, settings: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            return await self.api.async_fetch_questions(
                int(settings[CONF_AMOUNT]),
                settings.get(CONF_CATEGORY),
                settings.get(CONF_DIFFICULTY),
                settings.get(CONF_TYPE),
            )
        except OpenTDBTokenError:
            await self.api.async_reset_token()
            return await self.api.async_fetch_questions(
                int(settings[CONF_AMOUNT]),
                settings.get(CONF_CATEGORY),
                settings.get(CONF_DIFFICULTY),
                settings.get(CONF_TYPE),
            )
        except OpenTDBError as err:
            raise UpdateFailed(str(err)) from err

    @staticmethod
    def _prepare_question(question: dict[str, Any]) -> dict[str, Any]:
        answers = [question["correct_answer"], *question["incorrect_answers"]]
        for index in range(len(answers) - 1, 0, -1):
            swap = secrets.randbelow(index + 1)
            answers[index], answers[swap] = answers[swap], answers[index]
        return {**question, "answers": answers}

    def _player(self, user_id: str) -> dict[str, Any]:
        players = self._stored.setdefault("players", {})
        player = players.setdefault(
            user_id,
            self._new_player(user_id),
        )
        player.setdefault("session_id", secrets.token_urlsafe(16))
        return player

    def validate_session(self, user_id: str, session_id: str) -> None:
        """Reject session tokens that do not belong to the authenticated player."""
        if not secrets.compare_digest(self._player(user_id)["session_id"], session_id):
            raise ValueError("The quiz session is no longer valid")

    def _new_player(self, user_id: str) -> dict[str, Any]:
        now = dt_util.utcnow().isoformat()
        return {
            "index": 0,
            "answered": 0,
            "correct": 0,
            "points": 0,
            "streak": 0,
            "best_streak": 0,
            "answers": {},
            "stats": deepcopy(self._stored.setdefault("lifetime_stats", {}).get(user_id, {})),
            "started_at": now,
            "presented_at": now,
        }

    @staticmethod
    def _score_answer(player: dict[str, Any], correct: bool, now: datetime) -> tuple[int, int]:
        """Return (speed_bonus, streak_bonus) and update the player's streak in place."""
        if not correct:
            player["streak"] = 0
            return 0, 0
        presented = player.get("presented_at")
        if presented:
            elapsed = (now - datetime.fromisoformat(presented)).total_seconds()
        else:
            elapsed = SPEED_WINDOW_SECONDS
        speed_bonus = round(SPEED_BONUS_MAX * max(0.0, 1 - elapsed / SPEED_WINDOW_SECONDS))
        player["streak"] = player.get("streak", 0) + 1
        player["best_streak"] = max(player.get("best_streak", 0), player["streak"])
        streak_bonus = min(player["streak"], STREAK_BONUS_CAP) * STREAK_BONUS_STEP
        return speed_bonus, streak_bonus

    @staticmethod
    def _update_play_streak(lifetime: dict[str, Any], today: str) -> None:
        last = lifetime.get("last_played_date")
        if last == today:
            return
        yesterday = (datetime.fromisoformat(today).date() - timedelta(days=1)).isoformat()
        lifetime["daily_play_streak"] = (
            lifetime.get("daily_play_streak", 0) + 1 if last == yesterday else 1
        )
        lifetime["last_played_date"] = today

    def _player_name(self, user_id: str | None) -> str:
        if not user_id:
            return "Player"
        return self._stored.get("player_names", {}).get(user_id, "Player")

    def _record_completion(self, player: dict[str, Any]) -> None:
        stats = player.setdefault("stats", {})
        stats["quizzes_completed"] = stats.get("quizzes_completed", 0) + 1
        stats["percentage"] = (
            round(stats.get("correct", 0) / stats["questions"] * 100, 1)
            if stats.get("questions")
            else 0
        )
        self._stored.setdefault("lifetime_stats", {})[self._active_user or ""] = stats.copy()

    async def _save(self) -> None:
        await self.store.async_save(self._stored)

    def _build_view(self, user_id: str | None) -> dict[str, Any]:
        player = self._player(user_id) if user_id else {}
        questions = self._stored.get("questions", [])
        index = player.get("index", 0)
        complete = bool(player.get("complete"))
        question = (
            questions[index] if questions and index < len(questions) and not complete else None
        )
        public_question = None
        if question:
            public_question = {
                key: value for key, value in question.items() if key != "correct_answer"
            }
        answered = player.get("answered", 0)
        correct = player.get("correct", 0)
        state = (
            "idle"
            if not questions
            else "complete"
            if complete
            else "feedback"
            if player.get("feedback")
            else "question"
        )
        stats = player.get("stats", {})
        aggregate = {"questions": 0, "correct": 0, "quizzes_completed": 0}
        for stored_stats in self._stored.get("lifetime_stats", {}).values():
            for key in aggregate:
                aggregate[key] += stored_stats.get(key, 0)
        aggregate["percentage"] = (
            round(aggregate["correct"] / aggregate["questions"] * 100, 1)
            if aggregate["questions"]
            else 0
        )
        quiz_name = self.entry.data.get("quiz_name", "Open Trivia Database")
        feedback = deepcopy(player.get("feedback"))
        elapsed = self._elapsed_seconds(player)
        score = {
            "answered": answered,
            "correct": correct,
            "incorrect": answered - correct,
            "percentage": round(correct / answered * 100, 1) if answered else 0,
            "points": player.get("points", 0),
            "streak": player.get("streak", 0),
            "best_streak": player.get("best_streak", 0),
        }
        leaderboard = self._build_leaderboard()
        game = {
            "quiz_name": quiz_name,
            "day": (self._stored.get("created_at") or "")[:10],
            "total_questions": len(questions),
            "question": public_question,
            "score": score,
            "elapsed_seconds": elapsed,
            "player": {
                "name": self._player_name(user_id),
                "total_points": stats.get("total_points", 0),
                "daily_play_streak": stats.get("daily_play_streak", 0),
            },
            "leaderboard": leaderboard,
        }
        return {
            "session_id": player.get("session_id"),
            "state": state,
            "quiz_name": quiz_name,
            "set_id": self._stored.get("set_id"),
            "last_questions_reset": self._stored.get("created_at"),
            "question": public_question,
            "question_index": index,
            "total_questions": len(questions),
            "feedback": feedback,
            "score": score,
            "elapsed_seconds": elapsed,
            "player_stats": stats,
            "quiz_stats": aggregate,
            "leaderboard": leaderboard,
            "game": game,
        }

    def _build_leaderboard(self) -> list[dict[str, Any]]:
        today = dt_util.utcnow().date().isoformat()
        board: list[dict[str, Any]] = []
        for uid, stats in self._stored.get("lifetime_stats", {}).items():
            daily = stats.get("daily", {}).get(today, {})
            board.append(
                {
                    "name": self._player_name(uid),
                    "points_today": daily.get("points", 0),
                    "points_total": stats.get("total_points", 0),
                    "accuracy": stats.get("percentage", 0),
                    "best_streak": stats.get("best_streak", 0),
                }
            )
        board.sort(key=lambda entry: (entry["points_today"], entry["points_total"]), reverse=True)
        return board

    @staticmethod
    def _elapsed_seconds(player: dict[str, Any]) -> int:
        started = player.get("started_at")
        if not started:
            return 0
        ended = player.get("completed_at")
        finish = datetime.fromisoformat(ended) if ended else dt_util.utcnow()
        return max(0, int((finish - datetime.fromisoformat(started)).total_seconds()))
