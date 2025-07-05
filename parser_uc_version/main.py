import datetime
import pickle
import time
from typing import Dict, Union, List

import pytz
from loguru import logger
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

from config import ADMIN_CHAT_ID, BOT_NOTIFICATION
from parser_uc_version.chrome_driver import get_driver
from parser_uc_version.login import login_on_wb
from services.minio_server import minio_service
from services.postgres_server import db
from services.tg_bot_notif import send_notification_in_development_bot, alert_func
from wb_requests.get_suppliers_list_id import get_suppliers_idx

START_PAGE = 'https://seller.wildberries.ru/'
START_PAGE_DOMAIN = '.seller.wildberries.ru'

REPORT_PAGE = 'https://seller.wildberries.ru/suppliers-mutual-settlements/reports-implementations/reports-weekly'
REPORT_PAGE_DOMAIN = '.seller-weekly-report.wildberries.ru'

ADVERT_PAGE = 'https://cmp.wildberries.ru/campaigns/list/active'
ADVERT_PAGE_DOMAIN = 'cmp.wildberries.ru'

HISTORY_STOCKS_PAGE = 'https://seller.wildberries.ru/content-analytics/history-remains'
HISTORY_STOCKS_PAGE_DOMAIN = '.seller-content.wildberries.ru'


def get_cookies_from_wb(bot: Dict[str, Union[str, int]]) -> None:
    """
    Алгоритм получения куки токенов из кабинетов селлеров
    """
    logger.info(f"Инициализация номера {bot.get('phone')}")
    driver = get_driver()
    driver.get(START_PAGE)
    logger.info("Попытка открыть стартовую страницу")
    actions = ActionChains(driver)
    time.sleep(10)
    # driver.maximize_window()
    # driver.execute_script("document.body.style.zoom = '70%'")
    try:
        minio_service.get_obj(bot.get('phone'), f"data/cookies/{bot.get('phone')}")
        for cookie in pickle.load(open(f"data/cookies/{bot.get('phone')}", "rb")):
            driver.add_cookie(cookie)
        logger.info("Аутентификация по сохраненным кукам")

    except:
        logger.error('Куки недоступны, повторная аутентификация')
        login_on_wb(driver, bot)

    ### для внутренних тестов
    # cookies = [{'domain': '.wildberries.ru', 'expiry': 1735431222, 'httpOnly': False, 'name': 'x-supplier-id-external',
    #             'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': '96f2344d-2ca0-5ce0-b233-fea365ad86a3'},
    #            {'domain': 'seller.wildberries.ru', 'expiry': 1735431222, 'httpOnly': False, 'name': 'x-supplier-id',
    #             'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': '96f2344d-2ca0-5ce0-b233-fea365ad86a3'},
    #            {'domain': 'seller.wildberries.ru', 'expiry': 1702080821, 'httpOnly': True, 'name': 'WBToken',
    #             'path': '/', 'sameSite': 'None', 'secure': True,
    #             'value': 'AryGnhXi8ZDWDOLFpNcMU2aeQbznvy6Ur3ibWU-3Uc7rzl93xmRfMNFizUmOUucUkB_IcPwj1wvBi_-aIfLdhqqxuQTjaKTyG6vfHTZhgnakJV5lEbwOqSxeP9Ji8uxncAK0'},
    #            {'domain': '.wildberries.ru', 'expiry': 1735431222, 'httpOnly': False, 'name': 'external-locale',
    #             'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': 'ru'},
    #            {'domain': '.seller.wildberries.ru', 'expiry': 1732407197, 'httpOnly': False, 'name': '_wbauid',
    #             'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '10095212261696235501'},
    #            {'domain': 'seller.wildberries.ru', 'expiry': 1735431222, 'httpOnly': False, 'name': 'locale',
    #             'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': 'ru'}]
    # for cookie in cookies:
    #     driver.add_cookie(cookie)
    ###

    driver.get(START_PAGE)
    logger.info("Повторная попытка открыть стартовую страницу")
    if driver.current_url != START_PAGE:
        logger.info("Куки сгорели, осуществялется повторная аутентификация")
        login_on_wb(driver, bot)

    driver.execute_cdp_cmd('Network.enable', {})
    logger.info("Открыта стартовая страница")
    actions.scroll_by_amount(delta_x=0, delta_y=60).perform()
    time.sleep(5)
    WBToken_main: Dict = driver.get_cookie('WBToken').get('value')
    suppliers_ids_list: List[Dict[str, str]] = get_suppliers_idx(WBToken=WBToken_main)
    logger.info("Получен список продавцов")
    driver.get(REPORT_PAGE)
    logger.info("Открыта страница отчетов")
    time.sleep(10)
    actions.scroll_by_amount(delta_x=0, delta_y=60).perform()
    time.sleep(5)
    driver.get(HISTORY_STOCKS_PAGE)
    logger.info("Открыта страница истории остатков")
    time.sleep(10)
    actions.scroll_by_amount(delta_x=0, delta_y=60).perform()
    time.sleep(5)
    download_url = driver.find_elements(By.CSS_SELECTOR, "[class^='Button-link']")
    try:
        for i in download_url:
            if i.text == 'Загрузки':
                actions.move_to_element(i).click().perform()
                break
    except:
        for i in download_url:
            if i.text == 'Downloads':
                actions.move_to_element(i).click().perform()
                break
    time.sleep(10)
    actions.scroll_by_amount(delta_x=0, delta_y=60).perform()
    time.sleep(5)
    driver.get(ADVERT_PAGE)
    logger.info("Открыта страница с рекламой")
    time.sleep(10)
    actions.scroll_by_amount(delta_x=0, delta_y=60).perform()
    time.sleep(5)
    all_cookies = driver.execute_cdp_cmd('Network.getAllCookies', {}).get('cookies')
    logger.debug(f'Получены все куки сайта: {all_cookies}')
    try:
        WBToken_report = list(filter(lambda x: x['domain'] == REPORT_PAGE_DOMAIN, all_cookies))[0].get('value')
    except Exception as e:
        message = alert_func(e=e)
        send_notification_in_development_bot(chat_id=ADMIN_CHAT_ID, token=BOT_NOTIFICATION, message=message)
        WBToken_report = None
    try:
        WBToken_advert = list(filter(lambda x: x['domain'] == ADVERT_PAGE_DOMAIN, all_cookies))[0].get('value')
    except Exception as e:
        message = alert_func(e=e)
        send_notification_in_development_bot(chat_id=ADMIN_CHAT_ID, token=BOT_NOTIFICATION, message=message)
        WBToken_advert = None
    try:
        WBToken_history = list(filter(lambda x: x['domain'] == HISTORY_STOCKS_PAGE_DOMAIN, all_cookies))[0].get('value')
    except Exception as e:
        message = alert_func(e=e)
        send_notification_in_development_bot(chat_id=ADMIN_CHAT_ID, token=BOT_NOTIFICATION, message=message)
        WBToken_history = None

    time.sleep(10)
    for i_supplier in suppliers_ids_list:
        db.update_client_supplier_access(
            supplier_id=i_supplier.get('oldID'),
            insert_values={
                'cookie_wb_token': WBToken_main,
                'cookie_wb_token_report': WBToken_report,
                'cookie_wb_token_ads': WBToken_advert,
                'cookie_wb_token_sellers_analytics': WBToken_history,
                'cookie_x_supplier_id': i_supplier.get('id'),
                'updated_at': datetime.datetime.now(pytz.timezone('Europe/Moscow'))
            })
        logger.info(f"Добавлены токены по продавцу с supplier_id={i_supplier.get('oldID')}")
    message = 'Задача по сбору токенов завершена'
    send_notification_in_development_bot(chat_id=ADMIN_CHAT_ID, token=BOT_NOTIFICATION, message=message)

    driver.close()
    driver.quit()
