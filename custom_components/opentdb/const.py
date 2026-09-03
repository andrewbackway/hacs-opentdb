from typing import Final

DOMAIN: Final = "opentdb"
VERSION: Final = "0.1.0"
PLATFORMS: Final = ["sensor"]

CONF_QUIZ_NAME: Final = "quiz_name"
CONF_AMOUNT: Final = "amount"
CONF_CATEGORY: Final = "category"
CONF_DIFFICULTY: Final = "difficulty"
CONF_TYPE: Final = "type"
CONF_REFRESH_TIME: Final = "refresh_time"

DEFAULT_AMOUNT: Final = 10
DEFAULT_REFRESH_TIME: Final = "00:00:00"
MIN_AMOUNT: Final = 1
MAX_AMOUNT: Final = 50

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

STORAGE_VERSION: Final = 1
API_BASE: Final = "https://opentdb.com/api.php"
TOKEN_BASE: Final = "https://opentdb.com/api_token.php"
CATEGORIES_URL: Final = "https://opentdb.com/api_category.php"
