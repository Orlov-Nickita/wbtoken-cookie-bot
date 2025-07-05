import os.path
from typing import List, Dict
from loguru import logger
from playwright.sync_api import sync_playwright
from parser_playwright_version.play import get_cookies_from_wb_playwright
from services.postgres_server import db, engine
from tests.wbtoken_test import for_test__wbtoken
from icecream import ic


def initializer():
    """
    Проверяет, что подключения к базе данных родительского процесса не затронуты в новом пуле подключений
    """
    engine.dispose(close=False)


def main():
    """
    Основная функция запуска скрипта
    """
    if not os.path.exists('./data/cookies/'):
        os.makedirs('./data/cookies/')
    logger.debug("version v1.0")
    all_bot_phones: List[Dict[str, str]] = db.get_distinct_phones_from_all_cabinets_bot_activated()  # ok
    print(all_bot_phones)
    with sync_playwright() as playwright:
        for phone in all_bot_phones:
            get_cookies_from_wb_playwright(playwright=playwright, bot=phone, is_headless=False)
    logger.info("END")

#     for i_cab in cabinets:
#         ic(i_cab.get('cookie_x_supplier_id'))
# for_test__wbtoken(
#     cabinet_id=i_cab.get('id'),
#     WBToken=i_cab.get('cookie_wb_token'),
#     x_supplier_id=i_cab.get('cookie_x_supplier_id'),
#     wbx_validation_key=i_cab.get('cookie_wbx_validation_key')
# )


if __name__ == "__main__":
    main()
    suppliers_in_DB = db.get_all_supplier_id_with_phone_activated(phone='+79311090210')
    pass
