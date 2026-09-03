from __future__ import annotations

from html import unescape
import logging
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import API_BASE, CATEGORIES_URL, TOKEN_BASE

_LOGGER = logging.getLogger(__name__)


class OpenTDBError(Exception):
    """Base error for OpenTDB failures."""


class OpenTDBCannotConnectError(OpenTDBError):
    """The OpenTDB API could not be reached."""


class OpenTDBInvalidResponseError(OpenTDBError):
    """The OpenTDB API returned an invalid response."""


class OpenTDBNoResultsError(OpenTDBError):
    """OpenTDB has no questions for the requested filters."""


class OpenTDBRateLimitError(OpenTDBError):
    """OpenTDB rate-limited the request."""


class OpenTDBTokenError(OpenTDBError):
    """The OpenTDB session token is invalid or exhausted."""


class OpenTDBClient:
    def __init__(self, session: ClientSession) -> None:
        self._session = session
        self._token: str | None = None

    async def async_get_categories(self) -> list[dict[str, Any]]:
        payload = await self._async_json(CATEGORIES_URL)
        categories = payload.get("trivia_categories")
        if not isinstance(categories, list):
            raise OpenTDBInvalidResponseError("Missing trivia categories")
        return categories

    async def async_get_token(self) -> str:
        payload = await self._async_json(TOKEN_BASE, params={"command": "request"})
        if payload.get("response_code") != 0 or not payload.get("token"):
            raise OpenTDBTokenError("Could not create an OpenTDB token")
        self._token = str(payload["token"])
        return self._token

    async def async_reset_token(self) -> None:
        if self._token is None:
            return
        try:
            await self._async_json(
                TOKEN_BASE,
                params={"command": "reset", "token": self._token},
            )
        finally:
            self._token = None

    async def async_fetch_questions(
        self,
        amount: int,
        category: str | None = None,
        difficulty: str | None = None,
        type_: str | None = None,
    ) -> list[dict[str, Any]]:
        if self._token is None:
            await self.async_get_token()

        params: dict[str, Any] = {"amount": amount, "token": self._token}
        if category:
            params["category"] = category
        if difficulty:
            params["difficulty"] = difficulty
        if type_:
            params["type"] = type_

        payload = await self._async_json(API_BASE, params=params)
        response_code = payload.get("response_code")
        if response_code == 1:
            raise OpenTDBNoResultsError("No questions match the selected filters")
        if response_code in (3, 4):
            self._token = None
            raise OpenTDBTokenError("OpenTDB token is invalid or exhausted")
        if response_code == 5:
            raise OpenTDBRateLimitError("OpenTDB rate limit exceeded")
        if response_code != 0 or not isinstance(payload.get("results"), list):
            raise OpenTDBInvalidResponseError("Invalid question response")

        return [self._decode_question(item) for item in payload["results"]]

    async def _async_json(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            async with self._session.get(url, params=params) as response:
                response.raise_for_status()
                payload = await response.json()
        except (ClientError, ValueError) as err:
            _LOGGER.debug("OpenTDB request failed: %s", err)
            raise OpenTDBCannotConnectError from err
        if not isinstance(payload, dict):
            raise OpenTDBInvalidResponseError("Response was not an object")
        return payload

    @staticmethod
    def _decode_question(question: dict[str, Any]) -> dict[str, Any]:
        try:
            return {
                "category": unescape(str(question["category"])),
                "type": str(question["type"]),
                "difficulty": str(question["difficulty"]),
                "question": unescape(str(question["question"])),
                "correct_answer": unescape(str(question["correct_answer"])),
                "incorrect_answers": [
                    unescape(str(answer)) for answer in question["incorrect_answers"]
                ],
            }
        except (KeyError, TypeError) as err:
            raise OpenTDBInvalidResponseError("Question was missing required fields") from err
