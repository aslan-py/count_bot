from loguru import logger
from telebot import TeleBot
from telebot.types import Message

from app.constants import Tg, ValidationStatus
from app.service import main_service
from app.validators import ValidateData


class TeleBotConfig:
    """Настройки бота."""

    def __init__(self, token: str) -> None:
        """Создаем экземпляр бота внутри класса."""
        self.bot: TeleBot = TeleBot(token)
        logger.info('Экземпляр TeleBot успешно создан')

    def run(self) -> None:
        """Запуск бота в постоянному цикле."""
        logger.info('Бот запущен и слушает (infinity_polling)...')
        self.bot.infinity_polling()

    def _go_handler(self, message: Message) -> None:
        """Работа с командой go."""
        logger.info(
            f'Юзер {message.chat.id} ({message.from_user.first_name})'
            f'вызвал команду /go'
        )
        self.bot.send_message(message.chat.id, Tg.START)
        self.bot.register_next_step_handler(
            message, self._universal_step_handler, is_report=False
        )

    def _report_handler(self, message: Message) -> None:
        """Работа с командой report."""
        logger.info(
            f'Юзер {message.chat.id} (@{message.from_user.username}) '
            f'вызвал команду /report'
        )
        self.bot.send_message(
            message.chat.id, Tg.REPORT_WELCOME, parse_mode='HTML'
        )
        self.bot.register_next_step_handler(
            message, self._universal_step_handler, is_report=True
        )

    def _about_handler(self, message: Message) -> None:
        """Работа с командой About."""
        self.bot.send_message(
            message.chat.id, Tg.ABOUT, parse_mode=Tg.PARSE_MODE
        )

    def _unknown_handler(self, message: Message) -> None:
        """Работа со всеми остальными командами."""
        self.bot.send_message(
            message.chat.id,
            Tg.INCORRECT_MESSAGE.format(message.chat.first_name),
            parse_mode=Tg.PARSE_MODE,
        )

    def register_handlers(self) -> None:
        """Запускает хэнделры."""
        logger.debug('Регистрация командных хэндлеров...')

        @self.bot.message_handler(commands=['about'])
        def _about(message: Message) -> None:
            """Слушает команду about."""
            self._about_handler(message)

        @self.bot.message_handler(commands=['go'])
        def _go(message: Message) -> None:
            """Слушает команду go."""
            self._go_handler(message)

        @self.bot.message_handler(commands=['report'])
        def _report(message: Message) -> None:
            """Слушает команду report."""
            self._report_handler(message)

        @self.bot.message_handler(
            content_types=[
                'text',
                'audio',
                'document',
                'photo',
                'sticker',
                'video',
                'voice',
                'location',
                'contact',
            ],
            func=lambda message: True,
        )
        def _unknown(message: Message) -> None:
            """Cлушает все сотальные команлды и типы данных. Заглушка."""
            self.bot.send_message(
                message.chat.id,
                Tg.INCORRECT_MESSAGE.format(message.chat.first_name),
                parse_mode=Tg.PARSE_MODE,
            )

    def _send_final_response(
        self, chat_id: int, message: Message, result: str, is_report: bool
    ) -> None:
        """Формирует ответ после отработчки серсиного слоя.

        - Проверяет кортеж с возмоджными ошибками и кладет в переменную.
        - Ответ для ошибок по отчетам.
        - Ответ  для успеха по отчетам.
        - Аналогично два разных ответа для успеха и ошибки по затратам.
        """
        is_error = result in Tg.FULL_ERRRORS_SCOPE

        if is_report:
            if is_error:
                text = f'<b>{result}</b>' if is_error else result
                self.bot.send_message(chat_id, text, parse_mode='HTML')
            else:
                final_text = (
                    f'{result}\n\n'
                    'Чтобы получить новый отчет, используйте /report\n'
                    'Чтобы продолжить запись трат, используйте /go'
                )
                self.bot.send_message(chat_id, final_text, parse_mode='HTML')
            return

        # Для трат
        if is_error:
            self.bot.send_message(
                chat_id, f'<b>{result}</b>', parse_mode='HTML'
            )
        else:
            self.bot.send_message(
                chat_id, Tg.SUCCES_TEXT_MSG.format(result), parse_mode='HTML'
            )

    def _universal_step_handler(
        self, message: Message, is_report: bool = False
    ) -> None:
        """Основной цикл ожидания данных пользователя после ввода команды /go.

        Валидирует данные через отдельный метод.
        Проверяет статусы ошибок(если есть) для формирования
            ответа пользователю.
        Если ошибок нет передает объект message на подготовку к отправке в
            сервсиный слой.

        Args:
            message (Message): Объект входящего сообщения от Telegram.
            is_report: флаг запроса на отчетность.

        """
        logger.debug(
            f'Вход в step_handler. Юзер: {message.chat.id} '
            f'(@{message.from_user.username}), is_report: {is_report}'
        )
        status = ValidateData.get_validation_status(
            message, is_report=is_report
        )

        if not is_report and status == ValidationStatus.NEED_REPORT:
            logger.info(
                f'Перехват перехода в отчеты для {message.chat.id}'
                f'(@{message.from_user.username})'
            )
            self._report_handler(message)
            return

        error_data = ValidateData.return_status(status)
        if error_data:
            logger.warning(
                f'Валидация не пройдена ({status}) для {message.chat.id} '
                f'(@{message.from_user.username})'
            )
            text, parse_mode = error_data
            self.bot.send_message(message.chat.id, text, parse_mode=parse_mode)

            if status == ValidationStatus.INVALID:
                self.bot.register_next_step_handler(
                    message, self._universal_step_handler, is_report=is_report
                )
            return

        self._common_business_logic(message, is_report=is_report)

        if not is_report:
            self.bot.register_next_step_handler(
                message, self._universal_step_handler, is_report=is_report
            )

    def _common_business_logic(
        self, message: Message, is_report: bool = False
    ) -> None:
        """Подготавливает данные и вызывает методы сервисного слоя.

        Логика работы:
            1. Извлекает идентификаторы пользователя и контент (текст/голос).
            2. Запрашивает у сервисного слоя обработку транзакции или отчета.
            3. Формирует финальный ответ пользователю отдельным методом.

        Args:
            message: Объект сообщения Telegram.
            is_report: флаг запроса на отчетность.

        Note:
            При возникновении ошибок в сервисном слое прерывает выполнение
            и отправляет уведомление пользователю.

        """
        chat_id = message.chat.id
        tg_id = message.from_user.id  # type: ignore
        first_name = message.from_user.first_name  # type: ignore
        text_data = None
        voice_data = None

        if message.content_type == 'text':
            text_data = message.text

        elif message.content_type == 'voice':
            logger.debug(
                f'Загрузка голоса {message.voice.file_id} для {chat_id} '
                f'(@{message.from_user.username})'
            )
            self.bot.send_chat_action(chat_id, 'record_audio')
            info = self.bot.get_file(message.voice.file_id)  # type: ignore

            if not info.file_path:
                logger.error(
                    f'Нет file_path для голоса {message.voice.file_id}. '
                    f'Юзер: {chat_id} (@{message.from_user.username})'
                )
                self.bot.send_message(
                    chat_id, Tg.CRIT_VOICE_ERROR, parse_mode=Tg.PARSE_MODE
                )
                return

            voice_data = self.bot.download_file(info.file_path)

        self.bot.send_chat_action(chat_id, 'typing')
        logger.debug(
            f'Запрос в MainService для {chat_id} '
            f'(@{message.from_user.username})'
        )

        result = main_service.work_with_message(
            tg_id=tg_id,
            first_name=first_name,
            text=text_data,
            voice_bytes=voice_data,
            is_report=is_report,
        )
        self._send_final_response(chat_id, message, result, is_report)
