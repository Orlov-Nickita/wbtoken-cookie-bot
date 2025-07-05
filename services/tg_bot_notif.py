import os
import traceback
from pathlib import Path
from typing import Union
import requests
from loguru import logger


def send_notification_in_development_bot(chat_id: Union[int, str], token: str, message: str) -> None:
    """
    Отправляет сообщение с паролем в тг-бот
    """
    base_url = 'https://api.telegram.org/bot{token}/sendMessage'
    params = {
        'chat_id': chat_id,
        'text': message,
    }
    try:
        resp = requests.get(
            url=base_url.format(token=token),
            params=params
        )
        if not resp.status_code == 200:
            logger.error(f'Ошибка в боте: {resp.text}')
    except Exception as Ex:
        logger.error(f'При отправке сообщения в тг-бот возникла ошибка: {Ex}')


def alert_func(e: Union[Exception, BaseException]) -> str:
    traceback_str = traceback.format_exc()
    traceback_list = traceback.extract_tb(e.__traceback__)
    base_dir = Path(__file__).parent.parent.parent
    for tb in traceback_list:
        relative_path = os.path.relpath(tb.filename, base_dir)
        lineno = tb.lineno
        function = tb.name
        traceback_line = f"ФАЙЛ: {relative_path} \nСТРОКА: {lineno} \nФУНКЦИЯ: {function}"
        message_text = (
            f'Ошибка в wb-cookie-token: \n{e} '
            f'\n\nОписание: \n{traceback_line} '
            f'\n\nTRACEBACK: \n{traceback_str} '
        )
        return message_text
