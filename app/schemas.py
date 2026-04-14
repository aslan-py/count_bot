from datetime import date

from pydantic import BaseModel, Field, field_validator, model_validator

from app.constants import ValidatorError


class ExpenseSchema(BaseModel):
    """Схема проверки расходов.

    {"items": [{"product": "свет", "price": 1600
    {"items": []}
    """

    category: str = Field()
    product: str = Field()
    price: int = Field()

    @field_validator('category', 'product')
    @classmethod
    def check_not_empty(cls, value: str) -> str:
        """Удаляем пробелы по краям и проверяем длину."""
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError(ValidatorError.SCHEMAS_STRIP_ER)
        return stripped_value


class ExpenseListSchema(BaseModel):
    """Список трат, обернутый в ключ items."""

    items: list[ExpenseSchema] = Field(min_length=1)


class DateRangeSchema(BaseModel):
    """Схема для валидного диапазона дат.

    {"start_date": null, "end_date": null}
    {"start_date": "1976-10-11", "end_date": "1976-10-11"}
    """

    start_date: date | None = Field(None)
    end_date: date | None = Field(None)

    @model_validator(mode='after')
    def validate_dates(self) -> 'DateRangeSchema':
        """Проверяем что не перепктаны дата начала и дата конца."""
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValueError(ValidatorError.SCHEMAS_DATE_VALID)
        return self
