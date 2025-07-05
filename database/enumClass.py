class StatusOfTokenLoading:
    """
    Статус загрузки токенов из куков
    """
    # При смене наименований обязательно проверить и внести соответствующие правки в код сборщика
    # данных в одноименный класс в сборщиках данных mp-runners-request/WBToken cookie bot
    NOT_FILLED_IN = 'NOT_FILLED_IN'
    COLLECTING = 'COLLECTING'
    LOADED = 'LOADED'
    ERROR = 'ERROR'
