import traceback

from app.constants import Tg
from app.loguru_config import LoguruStart
from app.telebot_config import TeleBotConfig


def main() -> None:
    """Главная функция дергающая методы."""
    LoguruStart().start_loguru()
    bot_app = TeleBotConfig(Tg.TOKEN_TELEGRAMM)
    bot_app.register_handlers()
    print('Бот успешно инициализирован. Запуск polling...')
    try:
        bot_app.run()
    except Exception:
        print('Критическая ошибка при работе бота:')
        traceback.print_exc()


if __name__ == '__main__':
    main()
