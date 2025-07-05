import datetime
import sys
import os.path
from typing import List, Dict
from loguru import logger
import pandas as pd
from pandas import DataFrame
from playwright.sync_api import sync_playwright
from config import ADMIN_CHAT_ID, BOT_NOTIFICATION
from parser_playwright_version.play import get_cookies_from_wb_playwright
from services.clickhouse import clickhouse_client
from services.postgres_server import db, engine
from parser_uc_version.main import get_cookies_from_wb
from services.redis_chan import send_update_to_websocket_cabinet
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
    logger.info(sys.argv)
    runner_name = sys.argv[1]
    logger.debug("version v1.0")
    if runner_name == 'UPDATE_SUPPLIER_ID':
        try:
            logger.info("Старт задачи по обновлению supplier_id в нашей БД")
            all_cabinets_without_supplier_id = db.get_all_cabinets_with_nullable_supplier_id()
            postgres_added = 0
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
                    postgres_added += 1
                    db.update_client_supplier_access(cabinet_id=i_cab.get('id'),
                                                     insert_values={'supplier_id': int(supplier_id)})
            message = f"Завершение задачи по обновлению supplier_id в нашей БД. Добавлено {postgres_added} записей"
            logger.info(message)
            send_notification_in_development_bot(chat_id=ADMIN_CHAT_ID, token=BOT_NOTIFICATION, message=message)

            all_cabinets_with_supplier_id = db.get_all_cabinets_with_supplier_id()
            ch_added = 0
            for i_cab in all_cabinets_with_supplier_id:
                supplier_id = i_cab.get('supplier_id')
                is_client = clickhouse_client.is_supplier_mamod_client(supplier_id=supplier_id)
                if not is_client:
                    ch_added += 1
                    icab = [{
                        'supplier_id': supplier_id,
                        'updated_at': datetime.datetime.now()
                    }]
                    result_f = pd.DataFrame(icab, columns=['supplier_id', 'updated_at'])
                    clickhouse_client.update_clickhouse(db_table='mamod_clients_all', df=result_f)

            message = f"Завершение задачи по добавлению supplier_id в ClickHouse. Добавлено {ch_added} записей"
            logger.info(message)
            send_notification_in_development_bot(chat_id=ADMIN_CHAT_ID, token=BOT_NOTIFICATION, message=message)

        except Exception as e:
            logger.error(e)
            message = alert_func(e=e)
            send_notification_in_development_bot(chat_id=ADMIN_CHAT_ID, token=BOT_NOTIFICATION, message=message)
    else:
        try:
            if runner_name == 'CHECK_PHONE_AND_SUPPLIER__PLAYWRIGHT':
                logger.debug("Старт задачи по проверке номера бота и пользователя")
                supplier_id = int(sys.argv[2])
                phone = {'phone': sys.argv[3]}
                logger.debug(f'supplier_id: {supplier_id}')
                logger.debug(f'phone: {phone}')
                with sync_playwright() as playwright:
                    return get_cookies_from_wb_playwright(playwright=playwright, bot=phone, is_headless=True,
                                                          check_phone_and_supplier=True, supplier_id=supplier_id)
            else:
                if not os.path.exists('./data/cookies/'):
                    os.makedirs('./data/cookies/')

                all_bot_phones: List[Dict[str, str]] = db.get_distinct_phones_from_all_cabinets_bot_activated()  # ok
                logger.info(f"Получено {all_bot_phones.__len__()} номеров для сбора токенов")
                # logger.info("Ожидание 10 секунд перед стартом")
                # time.sleep(60)  # Нужно для того, чтобы верхний скрипт успевал отработать, когда запросы идут через
                # вебхуки
                logger.info("Старт задачи по сбору токенов из cookies")

                if runner_name == 'UPDATE_WBTOKENS_FROM_COOKIES__PLAYWRIGHT':
                    for phone in all_bot_phones:
                        with sync_playwright() as playwright:
                            get_cookies_from_wb_playwright(playwright=playwright, bot=phone, is_headless=True)

                        suppliers_in_DB = db.get_all_supplier_id_with_phone_activated(phone=phone.get('phone'))
                        for i_supplier in suppliers_in_DB:
                            cabinets_ids = db.get_cabinet_id_by_supplier_id(supplier_id=i_supplier.get('supplier_id'),
                                                                            is_one=False)
                            for ids in cabinets_ids:
                                client_id = ids.get('client_id')
                                send_update_to_websocket_cabinet(user_id=client_id, room_group_name='cabinet_list_')
                                send_update_to_websocket_cabinet(user_id=client_id,
                                                                 room_group_name='cabinet_retrieve_')

                elif runner_name == 'UPDATE_WBTOKENS_FROM_COOKIES__UNDETECTED_CHROMEDRIVER':
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
