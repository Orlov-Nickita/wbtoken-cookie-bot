import zipfile
from urllib.parse import urlparse

import undetected_chromedriver as uc
from fake_useragent import UserAgent
from loguru import logger


def get_manifest_and_background(filename, proxy_host, proxy_port, proxy_user, proxy_pass) -> str:
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """
    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (proxy_host, proxy_port, proxy_user, proxy_pass)
    with zipfile.ZipFile(filename, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    return filename


def suppress_exception_in_del(uc):
    """
    Если не использовать эту функцию, то драйвер будет падать с исключением, потому что внутри библиотеки есть
    ошибка из-за которой метод del вызывается дважды и второй раз уже на отсутствующем объекте
    """
    old_del = uc.Chrome.__del__

    def new_del(self) -> None:
        try:
            old_del(self)
        except:
            pass

    setattr(uc.Chrome, '__del__', new_del)


def set_options_to_driver():
    """
    # --incognito: Запускает браузер в режиме инкогнито, чтобы не сохранять историю и данные сеанса.
    # --no-sandbox: Отключает использование песочницы, что может быть полезно при запуске контейнера в среде Docker.
    # --disable-gpu: Отключает использование графического процессора, что может быть полезно при запуске контейнера в среде Docker.
    # --disable-setuid-sandbox: Отключает использование setuid-песочницы.
    # --headless=new: Запускает браузер в режиме без графического интерфейса.
    # --disable-application-cache: Отключает кэширование приложений.
    # --ignore-certificate-errors: Игнорирует ошибки сертификатов SSL.
    # --allow-running-insecure-content: Разрешает запуск небезопасного контента.
    # --disable-extensions: Отключает установленные расширения браузера.
    # --disable-dev-shm-usage: Отключает использование /dev/shm для временного хранения данных браузера.
    """
    suppress_exception_in_del(uc)
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f'user-agent={UserAgent().random}')
    options.add_argument('--incognito')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--headless=new')
    options.add_argument('--disable-application-cache')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    # proxy = 'http://GRhFp2:jbHoWn@160.116.217.153:8000'
    proxy = 'http://TXoRFm:FBf0RY@46.161.44.207:9387'
    logger.debug(f"{proxy}")
    parsed_url = urlparse(proxy)
    filename = 'proxy_auth_plugin.zip'
    options.add_extension(
        get_manifest_and_background(
            filename=filename,
            proxy_host=parsed_url.hostname,
            proxy_port=parsed_url.port,
            proxy_user=parsed_url.username,
            proxy_pass=parsed_url.password
        )
    )
    return options


def get_driver():
    """
    Получаем готовый к использованию драйвер браузера Chrome
    """
    options = set_options_to_driver()
    return uc.Chrome(options=options)
