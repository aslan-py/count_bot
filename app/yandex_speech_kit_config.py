import requests

from app.constants import YandexAi


class YaKit:
    """Настрйока обработки голоса  и преврашения его в текст."""

    def _get_token(self) -> str:
        """Берет iam токен из памяти или запрашивает новый."""
        response = requests.post(
            YandexAi.YA_SPEECH_KIT_URL,
            json=YandexAi.YA_SPEECH_KIT_JSON,
            headers=YandexAi.YA_SPEECH_KIT_HEADERS,
        )
        response.raise_for_status()
        return response.json().get('iamToken')

    def voice_to_text(self, binary_code: bytes) -> str:
        """Конвертируем аудио (bytes) в текст (str)."""
        iam_token = self._get_token()

        response = requests.post(
            YandexAi.YA_URL,
            headers={
                'Authorization': f'Bearer {iam_token}',
                'Content-Type': 'application/octet-stream',
            },
            params={
                'folderId': YandexAi.YANDEX_FOLDER_ID,
                'lang': YandexAi.YA_LANG,
                'format': YandexAi.YA_FORMAT,
            },
            data=binary_code,
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get('result', '')


yakit = YaKit()
