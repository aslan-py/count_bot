from loguru import logger
from telebot.types import Message

from app.constants import Tg, ValidationStatus, ValidatorError


class ValidateData:
    """Валидации для класссов ми методов телеграмм."""

    @staticmethod
    def get_validation_status(
        message: Message, is_report: bool = False
    ) -> ValidationStatus:
        """Централизованная проверка всех типов входящих сообщений.

        0. Проверяем наличие данных внутри from_user(сущность класса Telebot).
        1. Пришла команда с типом "/" - выходим из сессии записи трат.
        2. Пришло слово отчет (из PIVOT_WORDS) выходим из сессии и сразу
            запускаем работу с отчетами. Игнор, если проверку просим для отчета
        3. Проверяем что тип данных голос или текст.
        4. Проверяем что пришел не пустой текст.
        5. Проверяем что пришел не пустой голос.
        """
        if not message.from_user:
            return ValidationStatus.USER_ERROR

        text = message.text
        message_type = message.content_type

        if text and text.startswith('/'):
            return ValidationStatus.STOP

        if not is_report:
            if text and text in Tg.PIVOT_WORDS:
                return ValidationStatus.NEED_REPORT

        if message_type not in {'text', 'voice'}:
            return ValidationStatus.INVALID

        if message_type == 'text' and not text:
            ValidationStatus.INVALID

        if message_type == 'voice' and not message.voice:
            ValidationStatus.INVALID

        return ValidationStatus.SUCCESS

    @staticmethod
    def return_status(
        status: ValidationStatus,
    ) -> tuple[str, str | None] | None:
        """Готовит нужное сообщение для отправки в зависимости от статуса.

        - Создает словарь с ключами = статусам и значениями равными тексту
            сообщения и настройке формате сообшения.
        - Прогоняет в цикле полученный статус по словарю с ключами и формирует
            ответ в ТГ с ошибкой передавая его в виде кортежа.
        """
        responses = {
            ValidationStatus.STOP: (Tg.STOP, Tg.PARSE_MODE),
            ValidationStatus.INVALID: (Tg.VOICE_OR_TEXT, None),
            ValidationStatus.USER_ERROR: (Tg.PROBLEM, Tg.PARSE_MODE),
        }
        if status in responses:
            text, parse_mode = responses[status]
            return text, parse_mode
        return None

    @staticmethod
    def validate_yandex_response(text: str) -> str | None:
        """Проверка что Яндекс вернул текст и не вернул пустоту."""
        if text is None:
            logger.error('Yandex SpeechKit вернул None вместо текста')
            return ValidatorError.YANDEX_ERROR

        if not str(text).strip():
            logger.warning('Yandex SpeechKit распознал тишину (пустой текст)')
            return ValidatorError.VOICE_EMPTY

        return None
