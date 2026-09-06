"""Load and normalise local question-set files (<config>/opentdb/*.json)."""

from __future__ import annotations

import json
import os
import secrets
from typing import TYPE_CHECKING, Any

from .const import MAX_FILE_BYTES, MAX_FILE_QUESTIONS, QUESTION_SETS_SUBDIR

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


class QuestionFileError(Exception):
    """Base error for a local question-set file."""


class QuestionFileNotFoundError(QuestionFileError):
    """The requested question file does not exist."""


class QuestionFileInvalidError(QuestionFileError):
    """The question file name, path, or contents are invalid."""


class QuestionFileEmptyError(QuestionFileError):
    """The question file contained no usable questions."""


def questions_dir(hass: HomeAssistant) -> str:
    """Return the allow-listed directory that holds question-set files."""
    return hass.config.path(QUESTION_SETS_SUBDIR)


<<<<<<< HEAD
def _ensure_dir(base_dir: str) -> None:
    os.makedirs(base_dir, exist_ok=True)


async def async_ensure_questions_dir(hass: HomeAssistant) -> None:
    """Create <config>/opentdb so users have a place to drop question files."""
    await hass.async_add_executor_job(_ensure_dir, questions_dir(hass))


=======
>>>>>>> 5baa7c07cdad200ecab53a4313c3359528963357
def _safe_path(base_dir: str, filename: str) -> str:
    """Resolve filename inside base_dir, rejecting traversal outside it."""
    if not filename or filename != os.path.basename(filename) or not filename.endswith(".json"):
        raise QuestionFileInvalidError("Invalid question file name")
    base_real = os.path.realpath(base_dir)
    resolved = os.path.realpath(os.path.join(base_real, filename))
    if os.path.commonpath([base_real, resolved]) != base_real:
        raise QuestionFileInvalidError("Question file is outside the allowed folder")
    return resolved


def list_question_files(base_dir: str) -> list[str]:
    """Return the sorted names of *.json files in base_dir (empty if missing)."""
    try:
        entries = os.listdir(base_dir)
    except (FileNotFoundError, NotADirectoryError):
        return []
    return sorted(
        name
        for name in entries
        if name.endswith(".json") and os.path.isfile(os.path.join(base_dir, name))
    )


def _read_file(path: str) -> str:
    if not os.path.isfile(path):
        raise QuestionFileNotFoundError("Question file was not found")
    if os.path.getsize(path) > MAX_FILE_BYTES:
        raise QuestionFileInvalidError("Question file is too large")
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def parse_question_set(raw: str) -> dict[str, Any]:
    """Parse the raw file text into a JSON object."""
    try:
        data = json.loads(raw)
    except (ValueError, TypeError) as err:
        raise QuestionFileInvalidError("File is not valid JSON") from err
    if not isinstance(data, dict):
        raise QuestionFileInvalidError("Question file must be a JSON object")
    return data


def _normalise_one(item: Any, topic: str, difficulty: str) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        return None
    text = item.get("question")
    options = item.get("options")
    answer = item.get("answer")
    if not isinstance(text, str) or not text.strip():
        return None
    if not isinstance(options, list) or len(options) < 2:
        return None
    options = [str(option) for option in options]
    if len(set(options)) != len(options):
        return None
    if not isinstance(answer, str) or answer not in options:
        return None
    return {
        "category": topic or "Local quiz",
        "type": "boolean" if len(options) == 2 else "multiple",
        "difficulty": difficulty or "medium",
        "question": text.strip(),
        "correct_answer": answer,
        "incorrect_answers": [option for option in options if option != answer],
    }


def normalise_question_set(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Map the file's {question, options, answer} shape to the internal shape."""
    questions = data.get("questions")
    if not isinstance(questions, list) or not questions:
        raise QuestionFileEmptyError("No questions found in the file")
    topic = str(data.get("topic") or "")
    difficulty = str(data.get("difficulty") or "")
    normalised = [
        prepared
        for item in questions[:MAX_FILE_QUESTIONS]
        if (prepared := _normalise_one(item, topic, difficulty)) is not None
    ]
    if not normalised:
        raise QuestionFileEmptyError("No valid questions found in the file")
    return normalised


def sample_questions(questions: list[dict[str, Any]], amount: int) -> list[dict[str, Any]]:
    """Return a random subset of `amount` questions (whole pool if amount >= pool)."""
    pool = list(questions)
    count = len(pool)
    limit = count if amount <= 0 or amount >= count else amount
    for index in range(limit):
        swap = index + secrets.randbelow(count - index)
        pool[index], pool[swap] = pool[swap], pool[index]
    return pool[:limit]


async def async_list_question_files(hass: HomeAssistant) -> list[str]:
    """List available question files without blocking the event loop."""
    return await hass.async_add_executor_job(list_question_files, questions_dir(hass))


async def async_load_question_file(hass: HomeAssistant, filename: str) -> list[dict[str, Any]]:
    """Read, validate, and normalise a question file from the allowed folder."""
    path = _safe_path(questions_dir(hass), filename)
    raw = await hass.async_add_executor_job(_read_file, path)
    return normalise_question_set(parse_question_set(raw))
