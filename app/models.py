from datetime import date

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, String, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)

from app.constants import ModelsSettings


class Base(DeclarativeBase):
    """Абстрактный класс моделей."""

    __abstract__ = True

    @declared_attr
    @classmethod
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class Login(Base):
    """Модель пользователя.

    Name: имя пользователя(username из телеграмм)
    tg_id: id пользователя в телеграмме
    """

    name: Mapped[str | None] = mapped_column(
        String(ModelsSettings.STR_LEN), unique=True, nullable=True
    )
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)


class Category(Base):
    """Категория товара."""

    title: Mapped[str] = mapped_column(
        String(ModelsSettings.STR_LEN), unique=True, nullable=False
    )
    expenses: Mapped[list['Expenses']] = relationship(
        back_populates='category'
    )


class Expenses(Base):
    """Категория товара.

    login_id : Связь с таблицей Login.
    category_id : Связь с таблицей категорий.
    price : Цена без копеек.
    product : Название продукта на который была сделана трата.
    """

    login_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('login.id', name='fk_expenses_login', ondelete='CASCADE'),
        index=True,
    )
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            'category.id', name='fk_expenses_category', ondelete='CASCADE'
        ),
    )
    price: Mapped[int] = mapped_column(Integer)
    product: Mapped[str] = mapped_column(String(ModelsSettings.STR_PROD_LEN))
    create_at: Mapped[date] = mapped_column(
        Date, default=func.current_date(), server_default=func.current_date()
    )
    category = relationship(
        'Category', back_populates='expenses', lazy='joined'
    )
