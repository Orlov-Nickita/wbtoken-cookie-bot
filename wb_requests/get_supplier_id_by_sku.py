from typing import Optional, Union

import requests
from fake_useragent import UserAgent
from loguru import logger
from ratelimit import sleep_and_retry, limits

basket = [
    {"min": 0, "max": 143, "basket": "basket-01.wb.ru"},
    {"min": 144, "max": 287, "basket": "basket-02.wb.ru"},
    {"min": 288, "max": 431, "basket": "basket-03.wb.ru"},
    {"min": 432, "max": 719, "basket": "basket-04.wb.ru"},
    {"min": 720, "max": 1007, "basket": "basket-05.wb.ru"},
    {"min": 1008, "max": 1061, "basket": "basket-06.wb.ru"},
    {"min": 1062, "max": 1115, "basket": "basket-07.wb.ru"},
    {"min": 1116, "max": 1169, "basket": "basket-08.wb.ru"},
    {"min": 1170, "max": 1313, "basket": "basket-09.wb.ru"},
    {"min": 1314, "max": 1601, "basket": "basket-10.wb.ru"},
    {"min": 1602, "max": 1655, "basket": "basket-11.wb.ru"},
    {"min": 1656, "max": 1919, "basket": "basket-12.wb.ru"},
    {"min": 1920, "max": 2045, "basket": "basket-13.wb.ru"},
]


def make_url_from_sku(sku: int) -> Optional[str]:
    """
    Получаем URL по номеру артикула для отправки запроса
    """
    sku = str(sku)
    vol, part = sku[:-5], sku[:-3]
    for b in basket:
        if b["min"] <= int(vol) <= b["max"]:
            index = b['basket']
            break
    else:
        message_text = f'SKU={sku}. Не удалось получить ссылку basket-<...>.wb.ru'
        logger.error(message_text)
        return 'None'

    url = f'https://{index}/vol{vol}/part{part}/{sku}/info/ru/card.json'
    return url


@sleep_and_retry
@limits(calls=3, period=3)
def get_supplier_id_from_wb_by_sku(sku: int) -> Union[int, dict, None]:
    """
    Получаем характеристики по карточке ВБ
    """
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Origin': 'https://www.wildberries.ru',
        'Referer': f'https://www.wildberries.ru/catalog/{sku}/detail.aspx',
        'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': "Windows",
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': UserAgent().random,
    }
    url = make_url_from_sku(sku=sku)
    logger.info(url)
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        return {}
    try:
        raw = response.json()
        supplier_id: Optional[int] = raw.get("selling", {}).get("supplier_id", None) if raw else None
        return supplier_id
    except Exception as e:
        logger.error(e)
