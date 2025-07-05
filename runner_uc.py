import multiprocessing
import sys
import os.path
import time
from multiprocessing import Pool
from typing import List, Dict
from loguru import logger
from pandas import DataFrame
from playwright.sync_api import sync_playwright

from config import ADMIN_CHAT_ID, BOT_NOTIFICATION
from parser_playwright_version.play import get_cookies_from_wb_playwright
from services.clickhouse import clickhouse_client
from services.postgres_server import db, engine
from parser_uc_version.main import get_cookies_from_wb
from services.tg_bot_notif import send_notification_in_development_bot, alert_func
from wb_requests.get_supplier_id_by_sku import get_supplier_id_from_wb_by_sku


def initializer():
    """
    Проверяет, что подключения к базе данных родительского процесса не затронуты в новом пуле подключений
    """
    engine.dispose(close=False)


def main():
    """
    Основная функция запуска скрипта
    """
    runner_name = sys.argv[1]

    if runner_name == 'UPDATE_SUPPLIER_ID':
        try:
            logger.debug("version v1.0")
            logger.info("Старт задачи по обновлению supplier_id в нашей БД")
            all_cabinets_without_supplier_id = db.get_all_cabinets_with_nullable_supplier_id()
            for i_cab in all_cabinets_without_supplier_id:
                nmid = db.get_sku_by_cabinet_id(cabinet_id=i_cab.get('id'))
                if not nmid:
                    logger.warning(f"У пользователя с кабинетом {i_cab.get('id')} нет добавленных товаров!")
                else:
                    supplier_id_df: DataFrame = clickhouse_client.get_supplier_id_by_sku(sku=nmid.get('nm_id'))
                    if len(supplier_id_df) > 0:
                        logger.info(f"SKU={nmid.get('nm_id')} есть в БД ClickHouse")
                        supplier_id = supplier_id_df.loc[0]['supplier_id']
                    else:
                        logger.warning(f"SKU={nmid.get('nm_id')} нет в БД ClickHouse !")
                        supplier_id = get_supplier_id_from_wb_by_sku(sku=nmid.get('nm_id'))
                    db.update_client_supplier_access(cabinet_id=i_cab.get('id'),
                                                     insert_values={'supplier_id': int(supplier_id)})
            logger.info("Завершение задачи по обновлению supplier_id в нашей БД")
        except Exception as e:
            logger.error(e)
            message = alert_func(e=e)
            send_notification_in_development_bot(chat_id=ADMIN_CHAT_ID, token=BOT_NOTIFICATION, message=message)

    if runner_name == 'UPDATE_WBTOKENS_FROM_COOKIES':
        logger.info("Ожидание 120 секунд перед стартом")
        # time.sleep(120)  # Нужно для того, чтобы верхний скрипт успевал отработать, когда запросы идут через вебхуки
        try:
            logger.info("Старт задачи по сбору токенов из cookies")
            if not os.path.exists('./data/cookies/'):
                os.makedirs('./data/cookies/')
            logger.debug("version v1.0")
            all_bot_phones: List[Dict[str, str]] = db.get_distinct_phones_from_all_cabinets_bot_activated()  # ok
            logger.info(f"Получено {all_bot_phones.__len__()} номеров для сбора токенов")
            # with Pool(initializer=initializer, processes=multiprocessing.cpu_count()) as pool:
            #     pool.map(get_cookies_from_wb, all_bot_phones)
            for phone in all_bot_phones:
                get_cookies_from_wb(phone)

            logger.info("Завершение задачи по сбору токенов из cookies")
        except Exception as e:
            logger.error(e)
            message = alert_func(e=e)
            send_notification_in_development_bot(chat_id=ADMIN_CHAT_ID, token=BOT_NOTIFICATION, message=message)
        finally:
            if os.path.exists('./proxy_auth_plugin.zip'):
                os.remove('./proxy_auth_plugin.zip')


if __name__ == "__main__":
    main()
