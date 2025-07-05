from urllib.parse import urlparse

from icecream import ic
import datetime
import json
from pathlib import Path
from typing import Dict, List, Union, Optional
import pytz
from fake_useragent import UserAgent
from loguru import logger
from requests import Response
from config import ADMIN_CHAT_ID, BOT_NOTIFICATION
from database.enumClass import StatusOfTokenLoading
from parser_playwright_version.login import login_on_wb_playwright
from services.minio_server import minio_service
import time
from playwright.sync_api import Playwright, _generated
from services.postgres_server import db
from services.proxy import get_proxy
from services.tg_bot_notif import send_notification_in_development_bot
from wb_requests.get_suppliers_list_id import get_suppliers_idx

WBX_VALIDATION_KEY_DOMAIN = '.wildberries.ru'

START_PAGE = 'https://seller.wildberries.ru/'
START_PAGE_DOMAIN = 'seller.wildberries.ru'

REPORT_PAGE = 'https://seller.wildberries.ru/suppliers-mutual-settlements/reports-implementations/reports-weekly'
REPORT_PAGE_DOMAIN = 'seller-weekly-report.wildberries.ru'

ADVERT_PAGE = 'https://cmp.wildberries.ru/campaigns/list/active'
ADVERT_PAGE_DOMAIN = 'cmp.wildberries.ru'

HISTORY_STOCKS_PAGE = 'https://seller.wildberries.ru/content-analytics/history-remains'
HISTORY_STOCKS_PAGE_DOMAIN = 'seller-content.wildberries.ru'

SUPPLIES_PAGE = 'https://seller.wildberries.ru/supplies-management/warehouses-limits'
SUPPLIES_PAGE_DOMAIN = 'seller-supply.wildberries.ru'

PROMOTION_PAGE = 'https://seller.wildberries.ru/dp-promo-calendar'
PROMOTION_PAGE_DOMAIN = 'discounts-prices.wildberries.ru'

BASE_DIR = Path(__file__).parent.parent


def get_token_from_cookies(
        domain: str, context: Union[_generated.BrowserContext, List], is_from_cookies: bool = False,
        is_token: bool = True
) -> Optional[str]:
    """
    Извлекает токен из куков
    """
    if is_token:
        marker = 'WBToken'
    else:
        marker = 'wbx-validation-key'

    if not is_from_cookies:
        cookies_mookies = context.cookies()
    else:
        cookies_mookies = context
    try:
        return list(filter(lambda x: x['domain'].__contains__(domain)
                                     and x['name'].__contains__(marker),
                           cookies_mookies))[0].get('value')
    except Exception as e:
        # message = alert_func(e=e)
        message = f'Не найден токен {marker} для {domain}'
        send_notification_in_development_bot(chat_id=ADMIN_CHAT_ID, token=BOT_NOTIFICATION, message=message)
        return None


def get_cookies_from_wb_playwright(
        playwright: Playwright, is_headless: bool, bot: Dict[str, Union[str, int]],
        check_phone_and_supplier: bool = False, supplier_id: int = False
) -> Optional[Response]:
    resp = Response()
    resp.status_code = 200
    logger.info(f"Инициализация номера {bot}")
    proxy = None
    if is_headless:
        proxy = urlparse(get_proxy().get('http'))
        proxy = {
            "server": f"http://{proxy.hostname}:{proxy.port}",
            "username": proxy.username,
            "password": proxy.password
        }
    browser = playwright.chromium.launch(
        headless=is_headless,
        devtools=True,
        downloads_path=BASE_DIR,
        chromium_sandbox=False,
        slow_mo=1,
        proxy=proxy
    )
    time.sleep(5)
    context = browser.new_context(
        ignore_https_errors=True,
        service_workers='block',
        java_script_enabled=True,
        bypass_csp=True,
        user_agent=UserAgent().random,
        is_mobile=False,
        proxy=proxy
    )
    page = context.new_page()

    devtools = context.new_cdp_session(page)
    devtools.send('Network.enable')
    logger.info("Попытка открыть стартовую страницу")
    page.goto(START_PAGE, wait_until='load', timeout=100000)
    time.sleep(5)
    try:
        minio_service.get_obj(bot.get('phone'), f"{BASE_DIR}/data/cookies/{bot.get('phone')}.json")
        with open(f"{BASE_DIR}/data/cookies/{bot.get('phone')}.json", "r") as cookies:
            cookies = json.loads(cookies.read())
            context.add_cookies(cookies)
        logger.info("Аутентификация по сохраненным кукам")

    except:
        logger.error('Куки недоступны, повторная аутентификация')
        login_on_wb_playwright(base_dir=BASE_DIR, page=page, context=context, bot=bot)

    logger.info("Повторная попытка открыть стартовую страницу")
    page.goto(START_PAGE, wait_until='load', timeout=100000)
    time.sleep(5)
    # with page.expect_request("https://seller.wildberries.ru/ns/orders/suppliers-home-page/v1/orders/getStat") as first:
    #     first_request = first.value
    #     print('first_request.all_headers()', first_request.all_headers())
    #     print()
    #     print('first_request.failure', first_request.failure)
    #     print()
    #     print('first_request.frame', first_request.frame)
    #     print()
    #     print('first_request.headers_array()', first_request.headers_array())
    #     print()
    #     print('first_request.is_navigation_request()', first_request.is_navigation_request())
    #     print()
    #     print('first_request.method', first_request.method)
    #     print()
    #     print('first_request.post_data', first_request.post_data)
    #     print()
    #     print('first_request.post_data_json', first_request.post_data_json)
    #     print()
    #     print('first_request.post_data_buffer', first_request.post_data_buffer)
    #     print()
    #     print('first_request.redirected_from', first_request.redirected_from)
    #     print()
    #     print('first_request.redirected_to', first_request.redirected_to)
    #     print()
    #     print('first_request.resource_type', first_request.resource_type)
    #     print()
    #     print('first_request.response()', first_request.response())
    #     print()
    #     print('first_request.sizes()', first_request.sizes())
    #     print()
    #     print('first_request.timing', first_request.timing)
    #     print()
    #     print('first_request.url', first_request.url)
    #     print()
    if page.url != START_PAGE:
        logger.info("Куки сгорели, осуществляется повторная аутентификация")
        login_on_wb_playwright(base_dir=BASE_DIR, page=page, context=context, bot=bot)

    logger.info("Открыта стартовая страница")

    try:
        page.locator("//button[contains(@class, 'SelectInput__lrisnicezH')]").hover()
        page.locator("li").filter(has_text="ИП Ремишевский А. Б.ИНН").locator("label").nth(1).click()
        time.sleep(3)
    except:
        pass

    # print(context.cookies())
    # cookies = devtools.send('Network.getAllCookies').get('cookies')
    # print()
    # print(cookies)
    wbx_validation_key = get_token_from_cookies(domain=WBX_VALIDATION_KEY_DOMAIN, context=context, is_token=False)
    WBToken_main = get_token_from_cookies(domain=START_PAGE_DOMAIN, context=context)

    suppliers_ids_list: List[Dict[str, str]] = get_suppliers_idx(WBToken=WBToken_main,
                                                                 wbx_validation_key=wbx_validation_key)
    logger.info(f"Получен список продавцов")
    ic(suppliers_ids_list)
    if check_phone_and_supplier and supplier_id:
        # Здесь просто проверка на то, что пользователь добавил к себе нашего бота
        old_ids = [old.get('oldID') for old in suppliers_ids_list]
        if supplier_id in old_ids:
            logger.info('Пользователь добавил телефон в ЛК')
            logger.info("RESULT - TRUE - RESULT")
            return resp
        else:
            logger.info('Пользователь не добавил телефон в ЛК')
            logger.info("RESULT - FALSE - RESULT")
            resp.status_code = 404
            return resp

    page.goto(REPORT_PAGE, wait_until='load', timeout=100000)
    logger.info("Открыта страница с отчетами")
    time.sleep(5)

    page.goto(HISTORY_STOCKS_PAGE, wait_until='load', timeout=100000)
    logger.info("Открыта страница с историей остатков")
    time.sleep(5)
    try:
        page.locator("span").filter(has_text="Загрузки").nth(1).click()
        time.sleep(2)
        page.locator("span").filter(has_text="Загрузки").nth(1).click()
        time.sleep(2)
    except:
        pass
    try:
        page.locator("span").filter(has_text="Downloads").nth(1).click()
        time.sleep(2)
        page.locator("span").filter(has_text="Downloads").nth(1).click()
        time.sleep(2)
    except:
        pass

    page.goto(SUPPLIES_PAGE, wait_until='load', timeout=100000)
    logger.info("Открыта страница с поставками")
    time.sleep(5)

    page.goto(PROMOTION_PAGE, wait_until='load', timeout=100000)
    logger.info("Открыта страница с акциями")
    time.sleep(5)

    page.goto(ADVERT_PAGE, wait_until='load', timeout=100000)
    logger.info("Открыта страница с рекламой")
    try:
        with page.expect_request("https://cmp.wildberries.ru/api/v3/balance") as first:
            first_request = first.value
            authorizev3 = first_request.all_headers().get('authorizev3')
    except:
        authorizev3 = None

    time.sleep(5)

    try:
        page.get_by_text("Продвижение").click()
    except:
        try:
            page.get_by_placeholder("999-99-99").click()
            login_on_wb_playwright(base_dir=BASE_DIR, page=page, context=context, bot=bot, is_advert_page=True)
            page.goto(ADVERT_PAGE, wait_until='load', timeout=100000)
            logger.info("Повторно открыта страница с рекламой")
            time.sleep(5)
        except:
            pass

    cookies = devtools.send('Network.getAllCookies').get('cookies')
    logger.debug(f'Получены все куки сайта')
    ic(cookies)

    WBToken_report = get_token_from_cookies(domain=REPORT_PAGE_DOMAIN, context=cookies, is_from_cookies=True)
    WBToken_advert = get_token_from_cookies(domain=ADVERT_PAGE_DOMAIN, context=cookies, is_from_cookies=True)
    WBToken_history = get_token_from_cookies(domain=HISTORY_STOCKS_PAGE_DOMAIN, context=cookies, is_from_cookies=True)
    WBToken_supply = get_token_from_cookies(domain=SUPPLIES_PAGE_DOMAIN, context=cookies, is_from_cookies=True)
    WBToken_promotion = get_token_from_cookies(domain=PROMOTION_PAGE_DOMAIN, context=cookies, is_from_cookies=True)

    # ---------------------
    tokens = {
        'cookie_wb_token': WBToken_main,
        'cookie_wb_token_report': WBToken_report,
        'cookie_wb_token_ads': WBToken_advert or authorizev3,
        'cookie_wb_token_sellers_analytics': WBToken_history,
        'cookie_wb_token_supplies': WBToken_supply,
        'cookie_wb_token_promotion': WBToken_promotion,
        'cookie_wbx_validation_key': wbx_validation_key,
        'headers_authorizev3_ads': authorizev3
    }
    filtered_tokens = {key: value for key, value in tokens.items() if value}
    excluded_tokens = {key: value for key, value in tokens.items() if not value}

    for i_supplier in suppliers_ids_list:
        insert_values = {
                **filtered_tokens,
                'cookie_x_supplier_id': i_supplier.get('id'),
                'collecting_status_of_cookie_wb_tokens': StatusOfTokenLoading.LOADED,
                'updated_at': datetime.datetime.now(pytz.timezone('Europe/Moscow'))
            }
        db.update_client_supplier_access(
            supplier_id=i_supplier.get('oldID'),
            insert_values=insert_values)

        cabinets_ids = db.get_cabinet_id_by_supplier_id(supplier_id=i_supplier.get('oldID'), is_one=False)
        for ids in cabinets_ids:
            cabinet_id = ids.get('id')
            client_id = ids.get('client_id')
            db.update_cabinet_extension(cabinet_id=cabinet_id, insert_values={
                'wbtoken_bot_phone_number_id': bot.get('id'),
                'is_wbtoken_bot_activated': True
            })

            db.customer_journey_update_by_user_id(user_id=client_id, values={
                'wb_token': bool(insert_values.get('cookie_wb_token', False)),
                'wb_token_advertising': bool(insert_values.get('cookie_wb_token_ads', False)),
                'x_supplier_id': bool(insert_values.get('cookie_x_supplier_id', False)),
                'wb_token_report': bool(insert_values.get('cookie_wb_token_report', False)),
                'wbx_validation_key': bool(insert_values.get('cookie_wbx_validation_key', False)),
                'authorizev3': bool(insert_values.get('headers_authorizev3_ads', False)),
            })

        logger.info(f"Добавлены токены продавцу с supplier_id={i_supplier.get('oldID')}")

    suppliers_in_bot = {old.get('oldID') for old in suppliers_ids_list}
    suppliers_in_DB = db.get_all_supplier_id_with_phone_activated(phone=bot.get('phone'))
    suppliers_in_DB = {i.get('supplier_id') for i in suppliers_in_DB}
    wrong_suppliers = suppliers_in_DB - suppliers_in_bot

    for sup_id in wrong_suppliers:
        cabinets_ids = db.get_cabinet_id_by_supplier_id(supplier_id=sup_id, is_one=False)
        for ids in cabinets_ids:
            cabinet_id = ids.get('id')
            db.update_cabinet_extension(cabinet_id=cabinet_id, insert_values={
                'wbtoken_bot_phone_number_id': None,
                'is_wbtoken_bot_activated': False
            })
        db.update_client_supplier_access(
            supplier_id=sup_id,
            insert_values={
                'collecting_status_of_cookie_wb_tokens': None
            }
        )

    message = (f"Задача по сбору токенов на номере {bot.get('phone')} завершена. \n\n"
               f"Обновлено {suppliers_ids_list.__len__()} кабинетов. \n\n"
               f"Список: {[old.get('oldID') for old in suppliers_ids_list]}. \n\n"
               f"Добавлено токенов: {filtered_tokens.__len__()}. \n\n"
               f"Не найдено токенов: {excluded_tokens.__len__()}. ")
    send_notification_in_development_bot(chat_id=ADMIN_CHAT_ID, token=BOT_NOTIFICATION, message=message)

    context.close()
    browser.close()
    return resp
