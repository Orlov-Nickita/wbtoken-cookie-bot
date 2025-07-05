"""
Модуль посвящен настройке класса Database для работы с базой данных
"""
from typing import Dict, List, Optional, Union
from sqlalchemy import ResultProxy, select


class DataBase:
    """
    Класс для настройки работы с Базой данных
    """

    def __init__(
            self,
            engine,
            table_wb_data_client_supplier_access,
            table_internal_analytics_cabinetextension,
            table_internal_analytics_simbankphonenumbers,
            table_internal_analytics_wbproductcard,
            table_home_clientsettings,
            table_customer_journey
    ):
        self.engine = engine
        self.table_wb_data_csa = table_wb_data_client_supplier_access
        self.table_ia_cabinetextension = table_internal_analytics_cabinetextension
        self.table_ia_simbankphonenumbers = table_internal_analytics_simbankphonenumbers
        self.table_ia_wbproductcard = table_internal_analytics_wbproductcard
        self.table_home_clientsettings = table_home_clientsettings
        self.table_customer_journey = table_customer_journey

    @staticmethod
    def __to_dict(
            model: ResultProxy, one: bool = False
    ) -> Union[List[Dict], Dict, bool]:
        """
        Преобразует полученные данные из базы данных в словарь с названиями полей в качестве ключей для удобства
        работы с данными. Параметр one используется для случаев, когда получаем одну запись из БД
        """
        columns = model.keys()
        model_dict = []

        if not one:
            for i_m in model.fetchall():
                model_dict.append(
                    dict(zip(columns, i_m))
                )
            return model_dict

        try:
            return dict(zip(columns, model.first()))
        except TypeError:
            return False

    def get_distinct_phones_from_all_cabinets_bot_activated(
            self
    ) -> Optional[List[Dict[str, Union[str, int]]]]:
        """
        Кабинеты, у которых подключен бот для сбора куки токенов
        """
        with self.engine.connect() as conn:
            cabinets_raw: ResultProxy = conn.execute(
                select(self.table_ia_cabinetextension, self.table_ia_simbankphonenumbers)
                .join(self.table_ia_simbankphonenumbers,
                      self.table_ia_simbankphonenumbers.c.id == self.table_ia_cabinetextension.c.wbtoken_bot_phone_number_id)
                .where(self.table_ia_cabinetextension.c.is_wbtoken_bot_activated == True)
                .with_only_columns(self.table_ia_simbankphonenumbers.c.phone, self.table_ia_simbankphonenumbers.c.id)
                .distinct(self.table_ia_simbankphonenumbers.c.phone)
            )
            return self.__to_dict(cabinets_raw)

    def update_client_supplier_access(
            self, insert_values: Dict, supplier_id: int = False, cabinet_id: int = False
    ) -> Optional[bool]:
        """
        Обновляет кабинет пользователя
        """
        if supplier_id:
            cond = self.table_wb_data_csa.c.supplier_id == supplier_id
        elif cabinet_id:
            cond = self.table_wb_data_csa.c.id == cabinet_id
        else:
            return False
        with self.engine.connect() as conn:
            conn.execute(
                self.table_wb_data_csa
                .update()
                .where(cond)
                .values(**insert_values)
            )
            conn.commit()

    def get_all_cabinets_with_nullable_supplier_id(
            self
    ) -> List[Dict[str, int]]:
        with self.engine.connect() as conn:
            cabinets_raw: ResultProxy = conn.execute(
                select(self.table_wb_data_csa)
                .where(self.table_wb_data_csa.c.supplier_id.is_(None))
                .with_only_columns(
                    self.table_wb_data_csa.c.id,
                )
            )
            return self.__to_dict(cabinets_raw)

    def get_all_cabinets_with_supplier_id(
            self
    ) -> List[Dict[str, int]]:
        with self.engine.connect() as conn:
            cabinets_raw: ResultProxy = conn.execute(
                select(self.table_wb_data_csa)
                .where(~self.table_wb_data_csa.c.supplier_id.is_(None))
                .with_only_columns(
                    self.table_wb_data_csa.c.supplier_id,
                )
            )
            return self.__to_dict(cabinets_raw)

    def get_sku_by_cabinet_id(
            self, cabinet_id: int
    ) -> Dict[str, int]:
        with self.engine.connect() as conn:
            cabinets_raw: ResultProxy = conn.execute(
                select(self.table_ia_wbproductcard)
                .where(self.table_ia_wbproductcard.c.cabinet_id == cabinet_id)
                .with_only_columns(self.table_ia_wbproductcard.c.nm_id)
                .distinct(self.table_ia_wbproductcard.c.nm_id)
            )
            return self.__to_dict(cabinets_raw, one=True)

    def testfunc_get_all_cabinets_by_bot_phone(
            self, phone: str
    ):
        with self.engine.connect() as conn:
            cabinets_raw: ResultProxy = conn.execute(
                select(self.table_ia_cabinetextension, self.table_ia_simbankphonenumbers)
                .join(
                    self.table_ia_simbankphonenumbers,
                    self.table_ia_simbankphonenumbers.c.id == self.table_ia_cabinetextension.c.wbtoken_bot_phone_number_id
                )
                .join(
                    self.table_wb_data_csa,
                    self.table_wb_data_csa.c.id == self.table_ia_cabinetextension.c.cabinet_id
                )
                .where(self.table_ia_simbankphonenumbers.c.phone == phone)
                .with_only_columns(
                    self.table_wb_data_csa.c.id,
                    self.table_wb_data_csa.c.cookie_wb_token,
                    self.table_wb_data_csa.c.cookie_x_supplier_id,
                    self.table_wb_data_csa.c.cookie_wbx_validation_key,
                    self.table_ia_simbankphonenumbers.c.phone,
                )
            )
            return self.__to_dict(cabinets_raw)

    def get_all_supplier_id_with_phone_activated(self, phone: str):
        with self.engine.connect() as conn:
            cabinets_raw: ResultProxy = conn.execute(
                select(self.table_ia_cabinetextension, self.table_ia_simbankphonenumbers)
                .join(
                    self.table_ia_simbankphonenumbers,
                    self.table_ia_simbankphonenumbers.c.id == self.table_ia_cabinetextension.c.wbtoken_bot_phone_number_id
                )
                .join(
                    self.table_wb_data_csa,
                    self.table_wb_data_csa.c.id == self.table_ia_cabinetextension.c.cabinet_id
                )
                .where(self.table_ia_simbankphonenumbers.c.phone == phone)
                .with_only_columns(
                    self.table_wb_data_csa.c.supplier_id,
                )
                .distinct(self.table_wb_data_csa.c.supplier_id)
            )
            return self.__to_dict(cabinets_raw)

    def update_cabinet_extension(self, cabinet_id: int, insert_values: Dict):
        with self.engine.connect() as conn:
            conn.execute(
                self.table_ia_cabinetextension
                .update()
                .where(self.table_ia_cabinetextension.c.cabinet_id == cabinet_id)
                .values(**insert_values)
            )
            conn.commit()

    def get_cabinet_id_by_supplier_id(self, supplier_id: int, is_one: bool = True):
        with self.engine.connect() as conn:
            cabinets_raw: ResultProxy = conn.execute(
                select(self.table_wb_data_csa)
                .join(self.table_home_clientsettings,
                      self.table_home_clientsettings.c.id == self.table_wb_data_csa.c.client_settings_id)
                .where(self.table_wb_data_csa.c.supplier_id == supplier_id)
                .with_only_columns(self.table_wb_data_csa.c.id, self.table_home_clientsettings.c.client_id)
            )
            return self.__to_dict(cabinets_raw, one=is_one)

    def _customer_journey_check_exists(self, user_id: int) -> bool:
        with self.engine.connect() as conn:
            cj_raw: ResultProxy = conn.execute(
                select(self.table_customer_journey)
                .where(self.table_customer_journey.c.user_id == user_id)
            )
            cj = self.__to_dict(cj_raw)
            if not cj:
                return False
            return True

    def customer_journey_create(self, user_id: int):
        with self.engine.connect() as conn:
            conn.execute(
                self.table_customer_journey
                .insert()
                .values(user_id=user_id,
                        cabinet_exists=True)
            )
            conn.commit()

    def customer_journey_update_by_user_id(self, user_id: int, values: Dict):
        if not self._customer_journey_check_exists(user_id=user_id):
            self.customer_journey_create(user_id=user_id)
        with self.engine.connect() as conn:
            conn.execute(
                self.table_customer_journey
                .update()
                .where(self.table_customer_journey.c.user_id == user_id)
                .values(**values)
            )
            conn.commit()
