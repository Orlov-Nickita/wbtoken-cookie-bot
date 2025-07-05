import requests
from loguru import logger


def for_test__wbtoken(cabinet_id: int, WBToken: str, x_supplier_id: str, wbx_validation_key: str):
    cookies = {
        'WBTokenV3': WBToken,
        'wbx-validation-key': wbx_validation_key,
        'x-supplier-id': x_supplier_id,
        'x-supplier-id-external': x_supplier_id,
    }
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-type': 'application/json',
        'Origin': 'https://seller.wildberries.ru',
        'Pragma': 'no-cache',
        'Referer': 'https://seller.wildberries.ru/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    json_data = {
        'params': {},
        'method': 'getBalance',
        'jsonrpc': '2.0',
        'id': 'json-rpc_57',
    }

    resp = requests.post(
        'https://seller.wildberries.ru/ns/balance/suppliers-home-page/api/v1/balance',
        cookies=cookies,
        headers=headers,
        json=json_data,
    )
    logger.debug(f'Кабинет {cabinet_id}. Статус {resp}')
    try:
        logger.info(f'Кабинет {cabinet_id}. Ответ {resp.json()}')
    except Exception as e:
        logger.warning(resp.text)
        logger.warning(f'Кабинет {cabinet_id}. WBToken={WBToken}, x_supplier_id={x_supplier_id}')
        logger.error(e)

#
# sup_idx = [
#     'bfd221b8-be56-40f4-b57c-8c584adc22f2',
#     '7f33b867-da33-435c-b9b3-74f00020a7d6',
#     '96f2344d-2ca0-5ce0-b233-fea365ad86a3',
#     '54ecae46-69d2-40f4-af21-f8eb077dc730',
# ]
# wbx_val = '60f0d015-720a-437d-8fc4-687e8c257aef'
# wbtoken = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDU1ODg1MTEsInZlcnNpb24iOjIsInVzZXIiOiIxMzYxOTYzMDkiLCJzaGFyZF9rZXkiOiIxNyIsImNsaWVudF9pZCI6InNlbGxlci1wb3J0YWwiLCJzZXNzaW9uX2lkIjoiMDgxMTc0MDNhZjE1NDA1ODk5ZjkwOTU1NTNmYTAyYzciLCJ1c2VyX3JlZ2lzdHJhdGlvbl9kdCI6MTcwMTk3MTYwNSwidmFsaWRhdGlvbl9rZXkiOiIwN2M5MzQzNmMxMWVkODk2ZGU2YTQzNjY2MzM1YTAxYzc3NjQ3NzkxODI3NDg3YmQyYmJhMTBlNWNjY2IyMzI3IiwicGhvbmUiOiJaUTZOS2crU3N1QVpCZmhlMmNSeFNRPT0ifQ.Hmjj_C18MFLbpOgRna53Hp4fLrSN8G8-QfzDEKUBoIh8tN9-fU001dhFv4hmcl-2abMJF5NrVoacSTX4mO1hz5rfF2n5r9Gk72JWKVhao9crlPDPGx-cQpw7ApCCmG-M3CfhMUn9H82xW7VBlCw58MQjWNPkWmBR4pswybJ6vmo4zJGznxektlsCDeX6FF75CqMNTgYBGhy76jAXbTdlzxZCmSs5OgiVdNax60-Fk4-9VCFrmrcBaBtBXcAw7hsqlSXIeqteSC44o4AJZeR7ma2hjSZNhpZ6PXAbHvavyI6k4SD8XsPOHz_zjuvrnMYCPFEJKLFW77209D2l0rsDnQ'
#
# for i in sup_idx:
#     for_test__wbtoken(cabinet_id=123, WBToken=wbtoken, wbx_validation_key=wbx_val, x_supplier_id=i)