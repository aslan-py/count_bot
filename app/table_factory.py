from prettytable import PrettyTable

from app.constants import ValidatorError
from app.models import Expenses


class TableFactory:
    """Сервис для создания текстовых таблиц из данных БД."""

    @staticmethod
    def create_expense_table(expenses: list['Expenses']) -> str:
        """Формирует текстовую таблицу для Telegram.

        Основные этапы:
        1. Инициализация: таблица со столбцами ('Категория', 'Товар', 'Цена').
        2. В цикле вытаскиваем данные из объектов БД и добавляем строки.
        3. Разделяем тысячи в цене пробелом для удобства чтения.
        4. Выравниваем текст по левому краю, а цены — по правому.
        5. Оборачиваем в тег <pre> для сохранения структуры в мессенджере.
        """
        table = PrettyTable()
        table.field_names = ['Категория', 'Товар', 'Цена']

        for exp in expenses:
            table.add_row([
                exp.category.title,
                exp.product,
                f'{exp.price:,.0f}'.replace(',', ' '),
            ])

        table.align['Категория'] = 'l'
        table.align['Товар'] = 'l'
        table.align['Цена'] = 'r'

        table.max_width['Категория'] = 15
        table.max_width['Товар'] = 20

        return f'<pre>{table.get_string()}</pre>'

    @staticmethod
    def create_report_table(report_data: list[tuple[str, int]]) -> str:
        """Формирует таблицу агрегированных трат по категориям.

        - Принимает список кортежей [('Категория', сумма), ...].
        - Считает общий итог за период.
        - Выравнивает категории по левому краю, суммы — по правому.
        - Оборачиваем в тег <pre> для сохранения структуры в мессенджере.
        """
        if not report_data:
            return ValidatorError.TABLE_ERROR_EMPTY

        table = PrettyTable()
        table.field_names = ['Категория', 'Сумма']

        total_sum = 0
        for category, amount in report_data:
            table.add_row([category, f'{amount:,.0f}'.replace(',', ' ')])
            total_sum += amount

        table.align['Категория'] = 'l'
        table.align['Сумма'] = 'r'

        table.add_row(['-' * 15, '-' * 10])
        table.add_row(['ИТОГО', f'{total_sum:,.0f}'.replace(',', ' ')])

        return f'<pre>{table.get_string()}</pre>'


report = TableFactory()
