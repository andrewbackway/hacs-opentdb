from typing import Final

DOMAIN: Final = "opentdb"
VERSION: Final = "0.3.4"
PLATFORMS: Final = ["sensor"]

CONF_QUIZ_NAME: Final = "quiz_name"
CONF_AMOUNT: Final = "amount"
CONF_CATEGORY: Final = "category"
CONF_DIFFICULTY: Final = "difficulty"
CONF_TYPE: Final = "type"
CONF_REFRESH_TIME: Final = "refresh_time"
CONF_SOURCE: Final = "source"
CONF_FILE: Final = "file"

SOURCE_OPENTDB: Final = "opentdb"
SOURCE_FILE: Final = "file"

# Local question-set files live under <config>/opentdb/*.json
QUESTION_SETS_SUBDIR: Final = "opentdb"
MAX_FILE_BYTES: Final = 5 * 1024 * 1024
MAX_FILE_QUESTIONS: Final = 5000

DEFAULT_AMOUNT: Final = 10
DEFAULT_REFRESH_TIME: Final = "00:00:00"
MIN_AMOUNT: Final = 1
MAX_AMOUNT: Final = 50

# Game-show scoring
POINTS_BASE: Final = 100
SPEED_WINDOW_SECONDS: Final = 15
SPEED_BONUS_MAX: Final = 100
STREAK_BONUS_STEP: Final = 25
STREAK_BONUS_CAP: Final = 5

TYPE_ANY: Final = ""
TYPE_MULTIPLE: Final = "multiple"
TYPE_BOOLEAN: Final = "boolean"

DIFFICULTY_ANY: Final = ""
CATEGORY_ANY: Final = ""

SERVICE_START: Final = "start_quiz"
SERVICE_NEW: Final = "new_quiz"
SERVICE_ANSWER: Final = "submit_answer"
SERVICE_NEXT: Final = "next_question"
SERVICE_RESET: Final = "reset_quiz"
SERVICE_REFRESH: Final = "refresh"
SERVICE_REFRESH_QUESTIONS: Final = "refresh_questions"

STORAGE_VERSION: Final = 1
API_BASE: Final = "https://opentdb.com/api.php"
TOKEN_BASE: Final = "https://opentdb.com/api_token.php"
CATEGORIES_URL: Final = "https://opentdb.com/api_category.php"
