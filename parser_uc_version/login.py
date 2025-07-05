import pickle
import time
from loguru import logger
from selenium.webdriver.common.by import By
from config import EXTENSION_ID
from services.minio_server import minio_service
from services.telphin import get_code_from_wb_sms


def login_on_wb(driver, bot) -> None:
    """
    Осуществляется аутентификация на сайте WB
    """
    logger.info("Аутентификация")
    time.sleep(10)
    # input_frame = driver.find_element(By.CSS_SELECTOR, 'input[class^="SimpleInput"]')
    input_frame = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="999 999 99 99"]')
    input_frame.send_keys(bot.get('phone').replace('+7', ''))
    input_frame.submit()
    time.sleep(5)
    code: str = get_code_from_wb_sms(ext_id=EXTENSION_ID)
    logger.info("Получен код из смс")
    time.sleep(5)
    sms_pass_input = driver.find_elements(By.CSS_SELECTOR, 'input[inputmode="numeric"][autocomplete="new-password"]')
    for index, cube in enumerate(sms_pass_input):
        digit = code[index]
        cube.send_keys(digit)
    time.sleep(10)
    logger.info("Выполнен вход в ЛК")
    pickle.dump(driver.get_cookies(), open(f"data/cookies/{bot.get('phone')}", "wb"))
    minio_service.put_object(bot.get('phone'), f"data/cookies/{bot.get('phone')}")
    logger.info("Сохранен файл cookie")
    time.sleep(5)
