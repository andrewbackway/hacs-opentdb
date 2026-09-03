from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import logging
import secrets
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
    STORAGE_VERSION,
)

_LOGGER = logging.getLogger(__name__)


class QuizDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Own one quiz set and the per-user progress for that set."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, api: OpenTDBClient) -> None:
        super().__init__(hass, _LOGGER, name=f"{DOMAIN}_{entry.entry_id}", config_entry=entry)
        self.entry = entry
        self.api = api
        self.store = Store(hass, STORAGE_VERSION, f"{DOMAIN}_{entry.entry_id}")
        self._stored: dict[str, Any] = {"version": STORAGE_VERSION, "players": {}, "lifetime_stats": {}}
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

    async def async_start_quiz(self, user_id: str) -> None:
        self.set_active_user(user_id)
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
        self._stored["players"][user_id] = self._new_player(user_id)
        stats = self._stored["players"][user_id]["stats"]
        stats["quizzes_started"] = stats.get("quizzes_started", 0) + 1
        self._stored.setdefault("lifetime_stats", {})[user_id] = stats.copy()
        await self._save()
        self.async_set_updated_data(self._build_view(user_id))

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
        player["feedback"] = {"correct": correct, "answer": answer}
        player["answered"] = player.get("answered", 0) + 1
        player["correct"] = player.get("correct", 0) + int(correct)
        lifetime = player.setdefault("stats", {})
        lifetime["questions"] = lifetime.get("questions", 0) + 1
        lifetime["correct"] = lifetime.get("correct", 0) + int(correct)
        lifetime["percentage"] = round(lifetime["correct"] / lifetime["questions"] * 100, 1)
        today = dt_util.utcnow().date().isoformat()
        week = dt_util.utcnow().date().isocalendar()
        week_key = f"{week.year}-W{week.week:02d}"
        lifetime.setdefault("daily", {}).setdefault(today, {"questions": 0, "correct": 0})
        lifetime["daily"][today]["questions"] += 1
        lifetime["daily"][today]["correct"] += int(correct)
        lifetime.setdefault("weekly", {}).setdefault(week_key, {"questions": 0, "correct": 0})
        lifetime["weekly"][week_key]["questions"] += 1
        lifetime["weekly"][week_key]["correct"] += int(correct)
        self._stored.setdefault("lifetime_stats", {})[user_id] = lifetime.copy()
        player.setdefault("answers", {})[str(question_index)] = {
            "correct": correct,
            "answered_at": dt_util.utcnow().isoformat(),
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
        return player

    def _new_player(self, user_id: str) -> dict[str, Any]:
        return {
            "index": 0,
            "answered": 0,
            "correct": 0,
            "answers": {},
            "stats": deepcopy(self._stored.setdefault("lifetime_stats", {}).get(user_id, {})),
            "started_at": dt_util.utcnow().isoformat(),
        }

    def _record_completion(self, player: dict[str, Any]) -> None:
        stats = player.setdefault("stats", {})
        stats["quizzes_completed"] = stats.get("quizzes_completed", 0) + 1
        stats["percentage"] = round(stats.get("correct", 0) / stats["questions"] * 100, 1) if stats.get("questions") else 0
        self._stored.setdefault("lifetime_stats", {})[self._active_user or ""] = stats.copy()

    async def _save(self) -> None:
        await self.store.async_save(self._stored)

    def _build_view(self, user_id: str | None) -> dict[str, Any]:
        player = self._player(user_id) if user_id else {}
        questions = self._stored.get("questions", [])
        index = player.get("index", 0)
        complete = bool(player.get("complete"))
        question = questions[index] if questions and index < len(questions) and not complete else None
        public_question = None
        if question:
            public_question = {key: value for key, value in question.items() if key != "correct_answer"}
        answered = player.get("answered", 0)
        correct = player.get("correct", 0)
        state = "idle" if not questions else "complete" if complete else "feedback" if player.get("feedback") else "active"
        stats = player.get("stats", {})
        aggregate = {"questions": 0, "correct": 0, "quizzes_completed": 0}
        for stored_stats in self._stored.get("lifetime_stats", {}).values():
            for key in aggregate:
                aggregate[key] += stored_stats.get(key, 0)
        aggregate["percentage"] = round(aggregate["correct"] / aggregate["questions"] * 100, 1) if aggregate["questions"] else 0
        return {
            "state": state,
            "quiz_name": self.entry.data.get("quiz_name", "Open Trivia Database"),
            "set_id": self._stored.get("set_id"),
            "question": public_question,
            "question_index": index,
            "total_questions": len(questions),
            "feedback": deepcopy(player.get("feedback")),
            "score": {"answered": answered, "correct": correct, "incorrect": answered - correct, "percentage": round(correct / answered * 100, 1) if answered else 0},
            "elapsed_seconds": self._elapsed_seconds(player),
            "player_stats": stats,
            "quiz_stats": aggregate,
        }

    @staticmethod
    def _elapsed_seconds(player: dict[str, Any]) -> int:
        started = player.get("started_at")
        if not started:
            return 0
        ended = player.get("completed_at")
        finish = datetime.fromisoformat(ended) if ended else dt_util.utcnow()
        return max(0, int((finish - datetime.fromisoformat(started)).total_seconds()))
