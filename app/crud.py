"""Модуль CRUD-операций для управления финансовыми данными.

Данный модуль инкапсулирует логику взаимодействия с базой данных через
    SQLAlchemy.
Основные задачи модуля:
1. Синхронизация сущностей: автоматическое создание пользователей (Login)
   и категорий (Category) при их первом упоминании в транзакциях.
2. Транзакционная запись: сохранение списков расходов, полученных
   после обработки LLM и валидации Pydantic-схемами.
3. Аналитическая выборка: агрегация данных по категориям и периодам
   для формирования итоговых отчетов.

Класс CRUDbot использует SessionLocal для управления циклом сессий БД.
"""

from typing import Sequence

from sqlalchemy import desc, func, select
from sqlalchemy.engine import Row

from app.db import SessionLocal
from app.models import Category, Expenses, Login
from app.schemas import DateRangeSchema, ExpenseListSchema


class CRUDbot:
    """Управление данными пользователей, категорий и расходов в БД."""

    def _get_user_id(self, tg_id: int, name: str) -> int:
        """Возвращает ID пользоветля.Создает запись, если tg_id отсутствует."""
        with SessionLocal() as session:
            user = session.execute(
                select(Login).where(Login.tg_id == tg_id)
            ).scalar_one_or_none()
            if not user:
                user = Login(tg_id=tg_id, name=name)
                session.add(user)
                session.commit()
                session.refresh(user)
            return user.id

    def _get_category_id(self, title: str) -> int:
        """Возвращает ID категории. Создает новую, если название не найдено."""
        with SessionLocal() as session:
            category = session.execute(
                select(Category).where(Category.title == title)
            ).scalar_one_or_none()
            if not category:
                category = Category(title=title)
                session.add(category)
                session.commit()
                session.refresh(category)
            return category.id

    def add_expenses(
        self, schemas_in: ExpenseListSchema, tg_id: int, name: str
    ) -> list[Expenses]:
        """Сохраняет список расходов из pydantic-схемы в базу данных."""
        login_id = self._get_user_id(tg_id, name)
        all_new_items = []
        with SessionLocal() as session:
            for item in schemas_in.items:
                category_id = self._get_category_id(item.category)
                new_expense = Expenses(
                    login_id=login_id,
                    category_id=category_id,
                    price=item.price,
                    product=item.product,
                )
                session.add(new_expense)
                all_new_items.append(new_expense)
            session.commit()
            for expense in all_new_items:
                session.refresh(expense)
            return all_new_items

    def get_expenses_report(
        self, schemas_in: DateRangeSchema, tg_id: int, name: str | None = None
    ) -> Sequence[Row[tuple[str, int]]]:
        """Получает из БД категорию и тотал затрат за указанный период.

        Return:
         - [('Продукты', 5000), ('Такси', 1200)] с сортировкой Я->A
         - [] если пользоватля не найдет по tg_id.

        """
        stmt = (
            select(Category.title, func.sum(Expenses.price).label('total'))
            .join(Expenses)
            .join(Login)
            .where(
                Login.tg_id == tg_id,
                Expenses.create_at.between(
                    schemas_in.start_date, schemas_in.end_date
                ),
            )
            .group_by(Category.title)
            .order_by(desc('total'))
        )
        with SessionLocal() as session:
            result = session.execute(stmt)
        return result.all()


crud_bot = CRUDbot()
