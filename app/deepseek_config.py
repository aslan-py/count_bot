"""Работа с Deepseek-распознает текст и приводит в нужный формат.

Класс DeepSeekAi на вход получает настройки  клиента для старта работы ИИ.

_get_completion - заготовка , которая делает запрос по API ключу, отправляет:
    Промт - для инструкций какого типа строку нужно получить.
    Текст пользователя - то что прогоняем через промт.

get_products- передаем в заглушку _get_completion промт и текст пользователя.
    На выходе получаем уже не str и список словарей через метод json.loads

get_dates - пользователь вводит дату как угодно, нейросеть её понимает в
    соответствии с промтом и возвращает дату в строковом формате '%Y-%m-%d'
"""

from datetime import datetime as dt

from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam

from app.constants import DeepSeek


class DeepSeekAi:
    """Настройки работы с Deepseek."""

    def __init__(self) -> None:
        """Добавляем клиента deepseek."""
        self.client = OpenAI(
            api_key=DeepSeek.DEEPSEEK_API_KEY,
            base_url=DeepSeek.DEEPSEEK_API_URL,
        )

    def _get_completion(
        self, messages: list[ChatCompletionMessageParam], max_tokens: int
    ) -> ChatCompletion:
        """Внутренний метод - отправляет запрос и получает результат -> str."""
        return self.client.chat.completions.create(
            model=DeepSeek.DEEPSEEK_MODEL,
            messages=messages,
            stream=False,
            temperature=DeepSeek.TEMPERATURE,
            max_tokens=max_tokens,
        )

    def get_products(self, user_text: str) -> str:
        """Метод получения данных по затратам в str формате.

        Формат затрат:
         - {"items": [{"product": "хлеб", "price": 100, "category": "еда"}
         - {"items": []}
        """
        messages: list[ChatCompletionMessageParam] = [
            {'role': 'system', 'content': DeepSeek.PROMPT_PRODUCTS},
            {'role': 'user', 'content': user_text},
        ]
        response = self._get_completion(messages, DeepSeek.MAX_TOKENS_PROD)
        content = response.choices[0].message.content
        return content.strip() if content else '[]'

    def get_dates(self, user_text: str) -> str:
        """Метод переводит дату введенную пользователем в нужный str формат.

        Формат даты:
         - {"start_date": "2026-10-10", "end_date": "2026-01-10"}
         - {"start_date": null, "end_date": null}
        """
        today = dt.now().strftime('%Y-%m-%d')
        system_prompt = DeepSeek.PROMT_DATES.format(today=today)
        messages: list[ChatCompletionMessageParam] = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_text},
        ]
        response = self._get_completion(messages, DeepSeek.MAX_TOKENS_DATE)
        content = response.choices[0].message.content
        return content.strip() if content else '[]'


deepseek = DeepSeekAi()
