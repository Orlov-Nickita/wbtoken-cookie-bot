from clickhouse_driver import Client
from typing import List, Union

from loguru import logger
from pandas import DataFrame

from config import CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_ALT_HOSTS
from services.tg_bot_notif import alert_func


class MetaClass(type):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        """Singelton Design Pattern"""

        if cls not in cls._instance:
            cls._instance[cls] = super(MetaClass, cls).__call__(*args, **kwargs)
            return cls._instance[cls]


class ClickHouseConfig(metaclass=MetaClass):
    def __init__(self, host: str, port: str, alt_hosts: List[str]) -> None:
        self.host = host
        self.port = port
        self.alt_hosts = alt_hosts


class ClickHouseData:
    def __init__(self, params) -> None:
        self.params = params
        self.settings = {
            "connect_timeout": 9999,
            "receive_timeout": 9999,
            "send_timeout": 9999,
            "columnar": True,
            "use_numpy": True,
            "compression": True,
        }
        self.client = Client(
            host=params.host,
            port=params.port,
            settings=self.settings,
            alt_hosts=",".join(params.alt_hosts),
        )

    def _insert_into_clickhouse(self, data, db_table: str) -> None:
        self.client.insert_dataframe(f"INSERT INTO {db_table} VALUES", data)

    def update_clickhouse(self, db_table: str, df: DataFrame):
        self._insert_into_clickhouse(df, db_table=db_table)

    def get_supplier_id_by_sku(self, sku: int) -> list:
        return self.client.query_dataframe(
            f"SELECT DISTINCT supplier_id FROM goods_all WHERE sku = {sku}"
        )

    def is_supplier_mamod_client(self, supplier_id: Union[str, int]):
        try:
            p = self.client.query_dataframe(f'SELECT * FROM mamod_clients_all WHERE supplier_id = {supplier_id}')
            if p.size > 0:
                return True
            return False
        except:
            return False


clickhouse_configure = ClickHouseConfig(
    host=CLICKHOUSE_HOST,
    port=CLICKHOUSE_PORT,
    alt_hosts=CLICKHOUSE_ALT_HOSTS
)
clickhouse_client = ClickHouseData(params=clickhouse_configure)
