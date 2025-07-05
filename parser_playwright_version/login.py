import json
import re
import time
from pathlib import Path
from typing import Dict, List
from loguru import logger
from playwright.sync_api import Page, BrowserContext
from config import EXTENSION_ID
from services.minio_server import minio_service
from services.telphin import get_code_from_wb_sms


def login_on_wb_playwright(base_dir: Path, page: Page, context: BrowserContext, bot: Dict, is_advert_page: bool = False) -> None:
    """
    Осуществляется аутентификация на сайте WB
    """
    logger.info("Аутентификация")
    if not is_advert_page:
        page.locator("form").filter(has_text=re.compile(r"^\+7$")).get_by_placeholder("999-99-99").click()  # .locator("form").filter(has_text=re.compile(r"^\+7$")).
        phone = bot.get('phone').replace('+7', '')
        page.locator("form").filter(has_text=re.compile(r"^\+7$")).get_by_placeholder("999-99-99").fill(phone)  # .locator("form").filter(has_text=re.compile(r"^\+7$")).
    else:
        page.get_by_placeholder("999-99-99").click()  # .locator("form").filter(has_text=re.compile(r"^\+7$")).
        phone = bot.get('phone').replace('+7', '')
        page.get_by_placeholder("999-99-99").fill(phone)  # .locator("form").filter(has_text=re.compile(r"^\+7$")).
    if not is_advert_page:
        page.locator("form").filter(has_text=phone[:3]).get_by_role("button").nth(1).click()
    else:
        page.get_by_role("button", name="Получить код").click()
    time.sleep(5)
    code: str = get_code_from_wb_sms(ext_id=EXTENSION_ID)
    logger.info("Получен код из смс")
    time.sleep(5)
    for index, digit in enumerate(code):
        if not is_advert_page:
            page.locator(f"li:nth-child({index + 1}) > .InputCell--7FpiE").fill(f"{digit}")
        else:
            page.locator(f"input:nth-child({index + 1})").fill(f"{digit}")
            # page.locator(f"li:nth-child({index + 1}) > .Input-cell--ih7cY").fill(f"{digit}")
    time.sleep(10)
    logger.info("Выполнен вход в ЛК")
    with open(f"{base_dir}/data/cookies/{bot.get('phone')}.json", "w") as f:
        cookies = context.cookies()
        f.write(json.dumps(cookies))
    minio_service.put_object(bot.get('phone'), f"{base_dir}/data/cookies/{bot.get('phone')}.json")
    logger.info("Сохранен файл cookie")
    time.sleep(5)
