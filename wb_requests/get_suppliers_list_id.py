from typing import Dict, List, Union
import requests
from fake_useragent import UserAgent
from loguru import logger


def get_suppliers_idx(WBToken: str, wbx_validation_key: str) -> List[Dict[str, Union[str, int]]]:
    """
    После того, как обеспечивается доступ в ЛК продавца WB, мы получаем токен аутентификации. По этому токену мы
    делаем запрос на получение всех доступных для текущего пользователя кабинетов.
    """

    cookies = {
        'WBTokenV3': WBToken,
        'wbx-validation-key': wbx_validation_key,
    }
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9',
        'Connection': 'keep-alive',
        'Content-type': 'application/json',
        'Origin': 'https://seller.wildberries.ru',
        'Referer': 'https://seller.wildberries.ru/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': UserAgent().random,
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    json_data = [
        {
            'method': 'getUserSuppliers',
            'params': {},
            'id': 'json-rpc_3',
            'jsonrpc': '2.0',
        }
    ]
    response = requests.post(
        'https://seller.wildberries.ru/ns/suppliers/suppliers-portal-core/suppliers',
        cookies=cookies,
        headers=headers,
        json=json_data,
    )
    resp: Dict = response.json()[0]
    suppliers = resp.get('result', {}).get('suppliers')
    suppliers_idx = [
        {
            'id': idx['id'],
            'oldID': idx['oldID']
        }
        for idx in suppliers
    ]
    return suppliers_idx
