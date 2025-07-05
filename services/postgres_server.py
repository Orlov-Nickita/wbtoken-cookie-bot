from sqlalchemy import MetaData, create_engine
from sqlalchemy.pool import NullPool

from config import PG_USER, PG_PASS, PG_HOST, PG_PORT, PG_NAME
from database.database import DataBase

engine = create_engine(
    f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_NAME}",
    poolclass=NullPool
)
meta = MetaData()
meta.reflect(bind=engine)

table_wb_data_client_supplier_access = meta.tables['wb_data_client_supplier_access']
table_internal_analytics_cabinetextension = meta.tables['internal_analytics_cabinetextension']
table_internal_analytics_simbankphonenumbers = meta.tables['internal_analytics_simbankphonenumbers']
table_internal_analytics_wbproductcard = meta.tables['internal_analytics_wbproductcard']
table_home_clientsettings = meta.tables['home_clientsettings']
table_customer_journey = meta.tables['customer_journey_customerjourney']

db = DataBase(
    engine,
    table_wb_data_client_supplier_access=table_wb_data_client_supplier_access,
    table_internal_analytics_cabinetextension=table_internal_analytics_cabinetextension,
    table_internal_analytics_simbankphonenumbers=table_internal_analytics_simbankphonenumbers,
    table_internal_analytics_wbproductcard=table_internal_analytics_wbproductcard,
    table_home_clientsettings=table_home_clientsettings,
    table_customer_journey=table_customer_journey
)
