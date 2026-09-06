# Open Trivia Database for Home Assistant

Configurable Open Trivia Database quizzes for Home Assistant. Each configured quiz is its own device with a primary Quiz sensor, a question-set reset timestamp, aggregate quiz statistics, and a leaderboard. You can add the integration more than once to run several independent quizzes.

Questions come from the [Open Trivia Database API](https://opentdb.com/) or from a local JSON file you provide. Answer choices are shuffled before they are exposed to Home Assistant.

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

<<<<<<< HEAD
You can configure one or more independent quiz devices. To add another quiz, select **Add integration** again and give it a different name. During setup, first choose a **question source**:
=======
The integration supports one configured quiz device. During setup, first choose a **question source**:
>>>>>>> 5baa7c07cdad200ecab53a4313c3359528963357

- **Online (OpenTDB)** — questions are downloaded from the OpenTDB API (name, count, filters, refresh time).
- **Local file** — questions are loaded from a JSON file you place in `<config>/opentdb/`.

<<<<<<< HEAD
Configure the quiz name, question count, filters, and daily refresh time during setup. Each quiz keeps its own question set, schedule, players, and leaderboard.
=======
Configure its name, question count, filters, and daily refresh time during setup.
>>>>>>> 5baa7c07cdad200ecab53a4313c3359528963357

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| **Quiz name** | Yes | `Trivia Quiz` | Name shown for the quiz device and its entities. |
| **Number of questions** | Yes | `10` | Number of questions in each set. Integer from `1` to `50`. |
| **Category** | No | Any category | OpenTDB category ID as a string, for example `9` for General Knowledge. Leave blank for any category. See the [OpenTDB category list](https://opentdb.com/api_category.php). |
| **Difficulty** | No | Any difficulty | `easy`, `medium`, or `hard`. Leave blank for any difficulty. |
| **Question type** | No | Any type | `multiple` for four choices or `boolean` for True/False. Leave blank for either type. |
| **Daily refresh time** | Yes | `00:00:00` | Time in 24-hour `HH:MM:SS` format at which a new shared question set is downloaded for the day. |

The selected question combination is checked against OpenTDB when the integration is configured. A category is an OpenTDB numeric ID, not a category name. OpenTDB can return fewer questions than requested when its database does not have enough matching questions.

### Local question files

Select the **Local file** source to run a quiz from your own questions instead of OpenTDB.

<<<<<<< HEAD
- Place `*.json` files in `<config>/opentdb/`. The integration creates this folder on startup, and the setup dialog lists the files found there.
=======
- Place `*.json` files in `<config>/opentdb/` (create the folder if it does not exist). The setup dialog lists the files found there.
>>>>>>> 5baa7c07cdad200ecab53a4313c3359528963357
- Each day, a random subset of **Number of questions** is drawn from the file's pool, so a large file gives fresh quizzes daily. Answer order is reshuffled.
- File format:

  ```json
  {
    "topic": "Science and Nature",
    "difficulty": "easy",
    "questions": [
      { "question": "How many legs does a horse have?", "options": ["2", "4", "6", "8"], "answer": "4" }
    ]
  }
  ```

  Each question needs a non-empty `question`, at least two unique `options`, and an `answer` that is one of the `options`. Two options are treated as True/False; invalid questions are skipped. `topic` and `difficulty` are optional metadata.

### Options

To change these values later, open the integration under **Settings > Devices & services**, select the quiz device, and choose **Configure**. You can also switch a quiz between the **Online (OpenTDB)** and **Local file** sources here. Changing options resets unfinished progress for all users of that quiz, but keeps lifetime statistics.

## Sensors

Each configured quiz creates one Home Assistant device and four sensors. Entity names are based on the quiz name, so a quiz named `Trivia Quiz` normally creates entities such as `sensor.trivia_quiz_quiz` and `sensor.trivia_quiz_last_questions_reset`. The exact entity ID can vary if it conflicts with an existing entity.

All sensors are updated from the same coordinator snapshot. The values below describe the public state and attributes; missing top-level entity attributes are omitted rather than exposed as `null`. The nested `game` payload can contain `null` values so cards can distinguish an empty field from a missing payload.

### Sensor reference

#### Quiz

- **State:** `idle`, `question`, `feedback`, or `complete`.
- **Attributes:**
  - `quiz_name`: configured quiz name.
  - `total_questions`: number of questions in the current set.
  - `game`: complete nested payload intended for dashboards and custom cards. It contains `quiz_name`, `day`, `total_questions`, `question`, `score`, `player`, and `leaderboard`.

The `game` object is convenient when a card needs the whole quiz state from one entity. The remaining aggregate sensors are better suited to automations and compact dashboard cards.

#### Last questions reset

- **State:** the date and time when the current shared question set was fetched.
- **Device class:** timestamp.
- **Value:** a timezone-aware ISO 8601 timestamp rendered by Home Assistant according to the user's locale.

This timestamp changes when `new_quiz`, `refresh_questions`, a scheduled daily refresh, or another forced question refresh replaces the shared set. It is shared by all players of the configured quiz. It remains empty until the first question set has been downloaded.

#### Quiz statistics

- **State:** aggregate questions answered by all players.
- **Attributes:** `questions`, `correct`, `quizzes_completed`, and `percentage`.

The aggregate is calculated from the stored lifetime statistics for every player connected to that quiz device.

#### Leaderboard

- **State:** number of players with leaderboard entries.
- **Attributes:** `leaderboard`, sorted by today's points and then lifetime points.

Each leaderboard entry has this shape:

```yaml
name: Alex
points_today: 250
points_total: 1250
accuracy: 80.0
best_streak: 5
```

### Example state

For an active quiz, the main quiz sensor has a compact state plus structured attributes:

```yaml
entity_id: sensor.trivia_quiz_quiz
state: question
attributes:
  quiz_name: Trivia Quiz
  total_questions: 10
  game:
    quiz_name: Trivia Quiz
    day: "2026-09-05"
    total_questions: 10
    question:
      category: General Knowledge
      type: multiple
      difficulty: easy
      question: What is the capital of France?
      answers: [Berlin, Madrid, Paris, Rome]
    score:
      answered: 2
      correct: 2
      incorrect: 0
      percentage: 100.0
      points: 250
      streak: 2
      best_streak: 2
    player:
      name: Alex
      total_points: 1250
      daily_play_streak: 3
    leaderboard: []
```

The Quiz sensor is the card's data source. Its nested `game` attribute contains the current question and answer choices, per-user score, elapsed time, feedback, player summary, and leaderboard. The standalone question, score, elapsed-time, and player-statistics entities are intentionally not created. Progress and statistics are stored in Home Assistant's storage and survive restarts. A player reset clears only that player's active session. Replacing the shared question set clears unfinished active sessions for all players but retains lifetime statistics.

## Lovelace card

The Lovelace card is maintained in the separate [OpenTDB card repository](https://github.com/andrewbackway/hacs-opentdb-card). Install that repository through HACS as a **Dashboard** repository, then add a **Manual** card with this YAML:

```yaml
type: custom:opentdb-card
entity: sensor.trivia_quiz_quiz
title: Evening trivia
```

The dashboard must run in a logged-in Home Assistant user context because quiz actions are user-specific. The card targets the remaining Quiz sensor and uses the integration's authenticated WebSocket commands; it does not query the removed standalone sensors.

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
