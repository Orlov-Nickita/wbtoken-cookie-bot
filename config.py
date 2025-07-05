"""
Модуль с настройками и переменными
"""
import logging
import os
import dotenv

logging.basicConfig(level=logging.INFO)
dotenv.load_dotenv()

PG_USER = os.environ["PG_USER"]
PG_PASS = os.environ["PG_PASS"]
PG_HOST = os.environ["PG_HOST"]
PG_PORT = os.environ["PG_PORT"]
PG_NAME = os.environ["PG_NAME"]

MINIO_ENDPOINT = os.environ["MINIO_ENDPOINT"]
MINIO_ACCESS_KEY = os.environ["MINIO_ACCESS_KEY"]
MINIO_SECRET_KEY = os.environ["MINIO_SECRET_KEY"]
MINIO_REGION = os.environ["MINIO_REGION"]

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST")
CLICKHOUSE_PORT = os.getenv("CLICKHOUSE_PORT")
CLICKHOUSE_ALT_HOSTS = [
    os.getenv("CLICKHOUSE_ALT_HOST_1"),
    os.getenv("CLICKHOUSE_ALT_HOST_2"),
    os.getenv("CLICKHOUSE_ALT_HOST_3"),
    os.getenv("CLICKHOUSE_ALT_HOST_4"),
    os.getenv("CLICKHOUSE_ALT_HOST_5"),
]

BOT_NOTIFICATION = os.getenv('BOT_NOTIFICATION')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

TELFIN_CLIENT_ID = os.getenv('TELFIN_CLIENT_ID')
TELFIN_CLIENT_SECRET = os.getenv('TELFIN_CLIENT_SECRET')
EXTENSION_ID= os.getenv('EXTENSION_ID')

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")
