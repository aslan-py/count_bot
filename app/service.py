from typing import Any

from loguru import logger

from app.constants import ValidatorError
from app.crud import crud_bot
from app.deepseek_config import deepseek
from app.schemas import DateRangeSchema, ExpenseListSchema
from app.table_factory import report
from app.validators import ValidateData
from app.yandex_speech_kit_config import yakit


class MainService:
    """Обработчик логики парсинга нейросетями и записаи в БД."""

    @staticmethod
    def _config_work_with_message(is_report: bool) -> tuple[Any, ...]:
        """Возвращает данные для обработки сообщения в зависимости от режима.

        Args:
            is_report: Флаг режима (True — отчет, False — запись трат).

        Returns:
            Кортеж со следующими элементами:
            - ai_func: Метод нейросети для парсинга текста.
            - ai_error: Ошибка при сбое нейросети.
            - schema_cls: Класс Pydantic-схемы для валидации.
            - schema_error: Ошибка при несовпадении схемы.
            - db_func: Метод CRUD для работы с базой данных.
            - db_error: Ошибка при сбое операции в БД.

        """
        return {
            True: (
                deepseek.get_dates,
                ValidatorError.DEEPSEEK_ERROR_DATES,
                DateRangeSchema,
                ValidatorError.SCHEMAS_ERROR_DATE,
                crud_bot.get_expenses_report,
                ValidatorError.DB_GET_REPORT,
                report.create_report_table,
                ValidatorError.TABLE_ERROR_DATES,
            ),
            False: (
                deepseek.get_products,
                ValidatorError.DEEPSEEK_ERROR,
                ExpenseListSchema,
                ValidatorError.SCHEMAS_ERROR,
                crud_bot.add_expenses,
                ValidatorError.DB_ERROR,
                report.create_expense_table,
                ValidatorError.TABLE_ERROR,
            ),
        }[is_report]

    def work_with_message(
        self,
        tg_id: int,
        first_name: str,
        text: str | None = None,
        voice_bytes: bytes | None = None,
        is_report: bool = False,
    ) -> str:
        """Обработчик сообщения из тг: AI-парсинг -> Валидация -> Сохранение.

        Процесс:
        1. Распаковываем кортеж из функции конфигуратора.
        2. Если аудио - отдаем на распознавание в Яндекс, превращаем в текст
            делаем валиадции.
        3. DeepSeek: Извлекает данные из сырого текста пользователя.
        4. Pydantic: Проверяет соответствие схемfv валидации.
        5. CRUD записывает транзакцию в БД.
        6. TableFactory - выводит в ТГ табличку с тратами.

        Args:
            text: Сырой текст сообщения от пользователя.
            tg_id: Telegram ID пользователя для поиска/создания в БД.
            first_name: Имя пользователя (нужно при создании нового профиля).
            voice_bytes: звуковое сообщение.
            is_report: запрос на отчетность или на парсинг тарт.

        """
        logger.info(f'Старт обработки сообщения. Юзер: {tg_id} ({first_name})')
        (
            ai_func,
            ai_err,
            schema,
            schema_err,
            crud_func,
            crud_err,
            report_func,
            report_err,
        ) = self._config_work_with_message(is_report)

        if voice_bytes:
            try:
                logger.debug(f'Конвертация голоса для {tg_id}')
                text = yakit.voice_to_text(voice_bytes)
                logger.debug(f'Распознанный текст: {text}')
                error = ValidateData.validate_yandex_response(text)
                if error:
                    return error
            except Exception:
                logger.exception('Ошибка при работе с Yandex SpeechKit/n/n')
                return ValidatorError.YANDEX_ERROR

        try:
            logger.debug(f'Отправка текста в AI ({ai_func.__name__}): {text}')
            deepseek_parsed_text = ai_func(text)
            logger.debug(f'Результат от AI: {deepseek_parsed_text}')
        except Exception:
            logger.exception(f'Ошибка deepseek {ai_func.__name__}')
            return ai_err

        try:
            valid_schemas = schema.model_validate_json(deepseek_parsed_text)
            logger.debug(
                f'Данные успешно валидированы по схеме {schema.__name__}'
            )
        except Exception:
            logger.error(
                f'Pydantic не смог собрать схему. Сырые данные: '
                f'{deepseek_parsed_text}'
            )
            return schema_err

        try:
            logger.debug(f'Вызов CRUD метода {crud_func.__name__} для {tg_id}')
            db_data = crud_func(valid_schemas, tg_id, first_name)
        except Exception:
            logger.exception(f'Ошибка БД при выполнении {crud_func.__name__}')
            return crud_err

        try:
            result = report_func(db_data)
            logger.info(f'Успешное завершение формирования отчета для {tg_id}')
            return result
        except Exception:
            logger.exception(
                f'Ошибка генерации таблицы в {report_func.__name__}'
            )
            return report_err


main_service = MainService()
