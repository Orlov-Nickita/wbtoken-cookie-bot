import re
from pytz import utc
from config import TELFIN_CLIENT_ID, TELFIN_CLIENT_SECRET
from datetime import datetime, timedelta
from typing import Union
import requests
import time
from loguru import logger


def get_token() -> Union[bool, str]:
    """
    Отправляет в АТС данные приложения (которое у них же и создавно для работы с АПИ), затем получает в ответе токен
    для доступа. Токен действует 1 час
    """
    data = {
        'grant_type': 'client_credentials',
        'client_id': TELFIN_CLIENT_ID,
        'client_secret': TELFIN_CLIENT_SECRET,
    }
    response = requests.post('https://apiproxy.telphin.ru/oauth/token', data=data)
    try:
        return response.json().get('access_token')
    except:
        return False


def get_code_from_wb_sms(ext_id: int) -> Union[str, bool]:
    """
    Делает запрос на телфин по ID очереди, находит смс от WB, затем извлекает код
    """
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://apiproxy.telphin.ru:443/api/ver1.0/extension/{ext_id}/message/?page=1&order=desc'
    now = (datetime.now(utc) - timedelta(seconds=20)).strftime("%Y-%m-%d %H:%M:%S")
    now = datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
    for i in range(0, 10):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response = response.json()
            for msg in response:
                if msg["src_num"] != "Wildberries":
                    continue
                msg_datetime = datetime.strptime(msg["init_time_gmt"], "%Y-%m-%d %H:%M:%S")
                if (
                        now < msg_datetime
                        and msg["src_num"] == "Wildberries"
                ):
                    code = re.findall(r'\b\d+\b', msg["text"])[0]
                    logger.info(f'Код подтверждения из смс: {code}')
                    return code
        time.sleep(2)
    return False
