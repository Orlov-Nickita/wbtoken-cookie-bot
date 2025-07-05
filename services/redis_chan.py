from asgiref.sync import async_to_sync
from channels_redis.core import RedisChannelLayer
from config import REDIS_DB, REDIS_PORT, REDIS_HOST


def send_update_to_websocket_cabinet(user_id: int, room_group_name: str):
    """
    ASGI-приложение, которое принимает запросы, написано под капотом основного приложения Django на базе
    Django Channels Rest Framework.
    """
    channel = RedisChannelLayer(hosts=[{'address': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'}])
    room = f'{room_group_name}{user_id}'
    async_to_sync(channel.group_send)(
        room, {
            'type': 'update_channel',
        }
    )
