# Open Trivia Database for Home Assistant

Configurable Open Trivia Database quizzes for Home Assistant. Each configured quiz is a separate device with sensors for the current question, score, elapsed time, player statistics, and aggregate quiz statistics.

Questions are fetched from the [Open Trivia Database API](https://opentdb.com/). The integration uses OpenTDB's default response encoding and shuffles answer choices before exposing them to Home Assistant.

## Installation

### One-click HACS installation

[![Open your Home Assistant instance and show the HACS integration dialog](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=andrewbackway&repository=hacs-opentdb&category=integration)

After HACS finishes downloading the integration:

1. Restart Home Assistant.
2. Open **Settings > Devices & services**.
3. Select **Add integration** and search for **Open Trivia Database**.
4. Complete the form and select **Submit**.

### Manual HACS installation

In HACS, open **Integrations**, select the three-dot menu, choose **Custom repositories**, and add:

```text
https://github.com/andrewbackway/hacs-opentdb
```

Choose **Integration** as the category, install it, restart Home Assistant, and add the integration from **Settings > Devices & services**.

## Configuration

Each config entry creates one quiz device. Multiple quizzes can be configured with different names and settings.

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| **Quiz name** | Yes | `Trivia Quiz` | Name shown for the device and its entities. Names must be unique. |
| **Number of questions** | Yes | `10` | Number of questions in each set. Integer from `1` to `50`. |
| **Category** | No | Any category | OpenTDB category ID as a string, for example `9` for General Knowledge. Leave blank for any category. See the [OpenTDB category list](https://opentdb.com/api_category.php). |
| **Difficulty** | No | Any difficulty | `easy`, `medium`, or `hard`. Leave blank for any difficulty. |
| **Question type** | No | Any type | `multiple` for four choices or `boolean` for True/False. Leave blank for either type. |
| **Daily refresh time** | Yes | `00:00:00` | Time in 24-hour `HH:MM:SS` format at which a new shared question set is downloaded for the day. |

The selected question combination is checked against OpenTDB when the integration is configured. A category is an OpenTDB numeric ID, not a category name. OpenTDB can return fewer questions than requested when its database does not have enough matching questions.

### Options

To change these values later, open the integration under **Settings > Devices & services**, select the quiz device, and choose **Configure**. Changing options resets unfinished progress for all users of that quiz, but keeps lifetime statistics.

## Sensors

The entity ID prefix is based on the quiz name. Home Assistant normally creates the following entities:

| Sensor | State | Attributes |
| --- | --- | --- |
| **Quiz** | `idle`, `question`, `feedback`, or `complete` | `game` (a self-contained payload consumed by the card: question, feedback, score, player, and leaderboard), plus `quiz_name`, `set_id`, `question_index`, `total_questions`, `feedback` |
| **Question** | Current question text | `category`, `type`, `difficulty`, `question`; `correct_answer` is intentionally omitted, and `answers` contains the shuffled choices |
| **Score** | Correct answers | `answered`, `correct`, `incorrect`, `percentage`, `points`, `streak`, `best_streak` |
| **Elapsed time** | Seconds since the quiz started | Unit: seconds (`s`) |
| **Player statistics** | Lifetime questions answered by the logged-in player | Player lifetime counters, percentage, `total_points`, `best_streak`, and `daily_play_streak` |
| **Quiz statistics** | Aggregate questions answered by all players | Aggregate counters and percentage |
| **Leaderboard** | Number of ranked players | `leaderboard` list ranked by points, each with `name`, `points_today`, `points_total`, `accuracy`, and `best_streak` |

The question sensor never exposes `correct_answer` while a question is active. Progress and statistics are stored in Home Assistant's storage and survive restarts. Statistics are maintained per Home Assistant user, while quiz statistics aggregate the stored player totals.

## Lovelace card

The Lovelace card is maintained in the separate [OpenTDB card repository](https://github.com/andrewbackway/hacs-opentdb-card). Install that repository through HACS as a **Dashboard** repository, then add a **Manual** card with this YAML:

```yaml
type: custom:opentdb-card
entity: sensor.trivia_quiz_quiz
title: Evening trivia
```

The dashboard must run in a logged-in Home Assistant user context because quiz actions are user-specific.

## Services

All services target a quiz **device** unless stated otherwise. In the UI, select the target device in **Developer tools > Actions**. The examples below show the equivalent YAML action syntax.

### Start or replace a quiz

`opentdb.start_quiz` starts or resumes the day's shared question set for the logged-in user, fetching a set only if none exists yet. `opentdb.new_quiz` force-fetches a brand-new shared set, replacing the current set and unfinished progress for every player. Lifetime statistics are always retained.

```yaml
action: opentdb.start_quiz
target:
  device_id: YOUR_QUIZ_DEVICE_ID
```

`opentdb.new_quiz` is the action behind a "new quiz" control.

### Submit an answer

`opentdb.submit_answer` accepts one answer for the current question. `question_index` is zero-based and `answer` must be the answer text from the question sensor's `answers` attribute.

```yaml
action: opentdb.submit_answer
target:
  device_id: YOUR_QUIZ_DEVICE_ID
data:
  question_index: 0
  answer: "The answer text"
```

Only one answer is accepted for a question. The action requires the quiz to be active and the index to match the current question.

### Move to the next question

`opentdb.next_question` advances the logged-in user's session. It only advances after feedback has been recorded.

```yaml
action: opentdb.next_question
target:
  device_id: YOUR_QUIZ_DEVICE_ID
```

### Reset a player's progress

`opentdb.reset_quiz` clears the logged-in user's current session without awarding quiz completion. It does not delete lifetime statistics.

```yaml
action: opentdb.reset_quiz
target:
  device_id: YOUR_QUIZ_DEVICE_ID
```

### Refresh published state

`opentdb.refresh` republishes the current state and does not replace questions or reset progress. Unlike the other services, it does not require an authenticated user. (The configured daily refresh time downloads a new shared question set automatically.)

```yaml
action: opentdb.refresh
target:
  device_id: YOUR_QUIZ_DEVICE_ID
```

### Refresh quiz questions

`opentdb.refresh_questions` is a deprecated alias of `opentdb.new_quiz`. It fetches a new question set and starts it for the logged-in user.
It replaces the current question set and unfinished progress for every player, while retaining
lifetime statistics.

```yaml
action: opentdb.refresh_questions
target:
  device_id: YOUR_QUIZ_DEVICE_ID
```

The `start_quiz`, `new_quiz`, `refresh_questions`, `submit_answer`, `next_question`, and `reset_quiz` actions require a logged-in Home Assistant user. Calls without a user context fail because the integration cannot identify which player's progress to change.

## OpenTDB limits and attribution

OpenTDB is a free external service. Its rate limits, availability, question coverage, and terms can change. If a request cannot be fulfilled, try fewer questions or broader filters. The integration does not require an API key.

Open Trivia Database content is provided under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/). OpenTDB's API is free to use and subject to its [current service terms](https://opentdb.com/api_config.php).

## Development

Run the Python checks with the project's configured tools:

```powershell
ruff check .
python -m pytest
```
