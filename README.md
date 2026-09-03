# Open Trivia Database for Home Assistant

A HACS custom integration that brings configurable Open Trivia Database quizzes into Home Assistant, with a bundled TypeScript Lovelace card.

Each quiz is configured as its own Home Assistant device. Configure the number of questions, category, difficulty, question type, and daily refresh time. The API request follows the OpenTDB configuration page and uses the default encoding.

## Install

Install this repository through HACS as an Integration, restart Home Assistant, then add **Open Trivia Database** from **Settings > Devices & services**.

## Card

Add the **Open Trivia Database Quiz** card and select the quiz sensor as its entity. The card shows one question at a time, submits one answer, displays short correct/incorrect feedback, and advances automatically. On completion it shows percentage and elapsed time.

## Services

The integration provides `opentdb.start_quiz`, `opentdb.new_quiz`, `opentdb.submit_answer`, `opentdb.next_question`, `opentdb.reset_quiz`, and `opentdb.refresh`. Answer and quiz-changing services use the logged-in Home Assistant user as the player identity.

Player progress, current sessions, lifetime totals, daily/weekly history, and aggregate quiz statistics are stored in Home Assistant storage and survive restarts. Historical statistics are retained indefinitely.

Open Trivia Database content is provided under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/). OpenTDB's API is free to use and subject to its current service terms and limits.
