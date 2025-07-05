from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_REGION
from minio import Minio


class MinioService:
    def __init__(self):
        self.client = Minio(
            endpoint=MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            region=MINIO_REGION,
            secure=False,
        )

    def put_object(self, obj_name, path):
        self.client.fput_object("wbtoken-cookie-bot", obj_name, path)

    def get_obj(self, obj_name, path):
        self.client.fget_object("wbtoken-cookie-bot", obj_name, path)


minio_service = MinioService()
