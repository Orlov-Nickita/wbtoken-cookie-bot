import requests


def get_proxy():
    response = requests.get(url="http://192.168.100.29:8111/get_proxy?proxy_for=cookie_bot")
    return response.json().get('proxy')
