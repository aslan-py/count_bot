import os
from enum import StrEnum

from dotenv import load_dotenv

load_dotenv()


class ValidationStatus(StrEnum):
    """Статусы для удобной работы с ошибками."""

    STOP = 'STOP'
    INVALID = 'INVALID'
    USER_ERROR = 'USER_ERROR'
    NEED_REPORT = 'NEED_REPORT'
    SUCCESS = 'SUCCESS'


class ModelsSettings:
    """Константы для настройки моделей и БД."""

    STR_LEN = 50
    STR_PROD_LEN = 100
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///count_bot.sqlite')


class DeepSeek:
    """Константы для настройки Deepseek."""

    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    DEEPSEEK_API_URL = 'https://api.deepseek.com'
    DEEPSEEK_MODEL = 'deepseek-chat'
    TEMPERATURE = 0.1
    MAX_TOKENS_PROD = 200
    MAX_TOKENS_DATE = 50
    PROMPT_PRODUCTS = """
    You are a financial assistant. Extract expenses from text.
    Return ONLY a JSON object with the key 'items'.

    [Rules]:
    - Format: {"items":
        [{"product": "name", "price": 0, "category": "category_name"}]}
    - ALWAYS correct spelling errors, typos, and slang in product names
        (e.g., 'хлиб' -> 'хлеб', 'пивас' -> 'пиво').
    - If category is not mentioned, INFER it based on the product
        name (e.g., 'milk' -> 'food').
    - If no products found, or not price foud return {"items": []}.
    - DO NOT wrap the output in
        markdown code blocks (e.g., do not use ```json or ```)

    [Example]:
    In: "купил хлеб за 100 и молоко за 80"
    Out: {"items": [{"product": "хлеб", "price": 100, "category": "еда"},
        {"product": "молоко", "price": 80, "category": "еда"}]}
    """

    PROMT_DATES = """
    You are a date extractor. Today is {today}.
    Extract start and end dates from text.

    [Rules]:
    - Return ONLY JSON:
        {{"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"}}
    - If no dates found, return {{"start_date": null, "end_date": null}}.
    - Single day: start_date and end_date are the same.
    - Missing year: use year from {today}.
    - No markdown, no prose.

    [Example]:
    In: "за неделю" (for today 2026-04-13) ->
        Out: {{"start_date": "2026-04-07", "end_date": "2026-04-13"}}
    In: "за месяц" (for today 2026-04-13) ->
        Out: {{"start_date": "2026-03-13", "end_date": "2026-04-13"}}
    In: "вчера" ->
        Out: {{"start_date": "2026-04-12", "end_date": "2026-04-12"}}
    In: "hello" -> Out: {{"start_date": null, "end_date": null}}
    """


class YandexAi:
    """Для настройки ЯндексИИ."""

    YA_SPEECH_KIT_URL = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    YA_SPEECH_KIT_JSON = {'yandexPassportOauthToken': os.getenv('AUTH')}
    YA_SPEECH_KIT_HEADERS = {'Content-Type': 'application/json'}
    YA_URL = 'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize'
    YANDEX_FOLDER_ID = os.getenv('FOLDER_ID')
    YA_LANG = 'ru-RU'
    YA_FORMAT = 'oggopus'


class LoguruSetup:
    """Для настроек Loguru."""

    DIR_NAME = 'logs'
    CONSOLE_FORMAT = (
        '{time:HH:mm:ss} | {level} | {module} | {function}| {message}'
    )
    LOG_NAME = 'log.log'
    ROTATION = '10 MB'
    RETENTION = 5
    LEVEL = 'INFO'
    LOG_FORMAT = (
        '{time:YYYY-MM-DD HH:mm:ss} | {level} | '
        '{module} | {function}| {message}'
    )
    ENCODING = 'utf-8'


class ValidatorError:
    """Константы для ошибок валидации."""

    DEEPSEEK_ERROR = (
        '⚠️ Ошибка нейросети Deepseek в распозновании текста затрат/nn.'
        'Попробуй еще раз, четко введи текстом(или голосом) сумму и трату.'
        'Если ошибка повторяется: призови на помощь Аслана.'
    )
    DEEPSEEK_ERROR_DATES = (
        '⚠️ Ошибка нейросети Deepseek в распозновании даты для отчёта./nn.'
        'Попробуй еще раз, четко введи дату начала и дату конца периода.'
        'Если ошибка повторяется: призови на помощь Аслана.'
    )
    SCHEMAS_ERROR = (
        '⚠️ Ошибка распознавания данных.\n\n'
        'Не удалось распознать данные(цена/товар).\n\n'
        'Нужно ввести название и цену. Попробуй еще раз.\n'
        'Если ошибка сохранится -призови на помощь Аслана..'
    )
    SCHEMAS_ERROR_DATE = (
        '⚠️ <b>Ошибка распознавания данных</b>\n\n'
        'Мне не удалось найти даты в твоем сообщении.\n\n'
        'Можешь написать: <i>"вчера"</i>, <i>"сегодня"</i>'
        'или указать числа, например: <i>"01.05 - 10.05"</i>. '
        'Попробуй еще раз!\n\n'
        'Если ошибка повторится — призови на помощь Аслана.'
    )
    SCHEMAS_STRIP_ER = (
        'Поле не может быть пустым или состоять только из пробелов'
    )
    SCHEMAS_DATE_VALID = 'Дата окончания не должна быть раньше даты начала'
    DB_ERROR = (
        '⚠️ Ошибка при записи в базу данных.\n\nПризови на помощь Аслана..'
    )
    DB_GET_REPORT = (
        '⚠️ Ошибка при попытке доcтать данные для отчета из БД.\n\n'
        'Призови на помощь Аслана..'
    )
    TABLE_ERROR = (
        '⚠️ Ошибка при формировании таблицы с затратами/n/n'
        '.Призови на помощь Аслана..'
    )
    TABLE_ERROR_DATES = (
        '⚠️ Ошибка при формировании отчета/n/n.Призови на помощь Аслана..'
    )
    TABLE_ERROR_EMPTY = 'За указанный период трат не найдено.'
    DEEPSEEK_EMPTY = (
        '<b>Недостаточно данных</b> 🧐\n\n'
        'Нужно ввести название и цену. Попробуй еще раз.'
    )
    VOICE_EMPTY = 'Запись голоса пришла пустой попробуй ещё раз...'
    YANDEX_ERROR = '⚠️ Ошибка нейросети Яндекс.Призови на помощь Аслана..'
    FULL_ERRRORS_SCOPE = (
        DEEPSEEK_ERROR,
        SCHEMAS_ERROR,
        DB_ERROR,
        TABLE_ERROR,
        DEEPSEEK_EMPTY,
        VOICE_EMPTY,
        YANDEX_ERROR,
        SCHEMAS_ERROR_DATE,
        DB_GET_REPORT,
        DEEPSEEK_ERROR_DATES,
        TABLE_ERROR_DATES,
        TABLE_ERROR_EMPTY,
        SCHEMAS_DATE_VALID,
    )


class Tg(ValidatorError):
    """Константы ддля телеграмм настроек."""

    TOKEN_TELEGRAMM = os.getenv('TOKEN_TELEGRAMM')
    ABOUT = """
    <b>🤖 Я — kitty_count_bot</b>

    <b>Веду учет финансов.</b>
    Пиши текст или отправляй голос.

    <b>Как вводить данные:</b>
    • <i>«Кофе 250»</i>
    • <i>«Бензин на 2000»</i>
    • <i>«Продукты 500, такси 300»</i>
    • <i>Либо надиктуй голосом затрату и стоимость</i>

    <b>Команды:</b>
    🚀 /go — начать работу.
    📊 <b>/report</b> — показать статистику
    ⛔ <b>stop</b> — завершить сессию
    """
    INCORRECT_MESSAGE = """
        Привет, <b>{}</b>! 🌚

        Чтобы начать работу, введи команду: /go
        Узнать о моих возможностях: /about
        """
    PARSE_MODE = 'HTML'
    START = (
        'Я готов к приёму данных как текстом, так и голосом.'
        '\n\nЕсли захочешь выйти из сессии, выбери в меню /stop'
    )
    REPORT_WELCOME = (
        '<b>📈 Добро пожаловать в царство отчетов!</b>\n\n'
        'Пришли даты начала и окончания периода.\n'
        '<i>Например: "с 1 по 10 мая" или "01.05 - 10.05"</i>\n\n'
        '🎤 <b>Псс...</b> Можно просто продиктовать даты голосом!\n\n'
        '💡 <i>После получения данных сессия закроется. '
        'Если потребуется новый отчет, введи <b>/report</b>.</i>'
    )
    STOP = (
        '<b>Сессия записи завершена</b>\n\n'
        '• Чтобы продолжить запись: /go\n'
        '• Чтобы открыть отчеты: /report'
    )
    VOICE_OR_TEXT = 'Жду только текст или голос.'
    PROBLEM = (
        '<b>⚠️ Ошибка доступа к данным</b>\n\n'
        'Не удалось извлечь информацию о пользователе. Вероятно, бот запущен в'
        ' канале или анонимной группе, где скрыты данные отправителя. '
        'В таких условиях корректная работа <b>невозможна</b>.\n\n'
        '<i>Если вы используете бота в личных сообщениях и видите эту ошибку, '
        'пожалуйста, сообщите об этом Аслану.</i>'
    )
    SUCCES_TEXT_MSG = (
        '<b>✅ Данные сохранены!</b>\n\n'
        '{}\n'
        '<i>Продолжайте ввод(можно голосом) или используйте /stop</i>'
    )
    PIVOT_WORDS = ('отчет', 'Отчет', 'ОТЧЕТ')
    PIVOT_ERR_MSG = (
        '🛑 <b>Сначала остановите ввод</b>\n\n'
        'Отчет будет доступен после команды /stop'
    )
    CRIT_VOICE_ERROR = (
        '🛑 <b>Ошибка в передаче голоса на стороне ТГ</b>\n\n'
        '• Либо ты ввел слишком длинную запись, попробуй сократить\n'
        '• Либо временный трубности на стороне ТГ, попробуй текстом ввести\n'
    )
