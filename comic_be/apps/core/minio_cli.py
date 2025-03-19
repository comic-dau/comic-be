import base64
import io
import mimetypes
import os
from urllib.parse import urlparse

import requests
from django.conf import settings
from loguru import logger
from minio import Minio, InvalidResponseError


class MinioStorage:
    def __init__(self):
        self.client = Minio(
            settings.STORAGE_URL,
            settings.STORAGE_ACCESS_KEY,
            settings.STORAGE_SECRET_KEY,
            secure=settings.STORAGE_SECURE,
        )
        self.domain = settings.STORAGE_URL

    def upload(self, bucket: str, filename: str, data: io.BytesIO, content_type: str, return_url: bool = False):

        data.seek(0)
        self.client.put_object(
            bucket_name=bucket,
            object_name=filename,
            data=data,
            length=data.getbuffer().nbytes,
            content_type=content_type
        )
        if return_url:
            return f"{self.domain}/{bucket}/{filename}"
        return None

    def upload_file(self, bucket: str, filename: str, file_obj, return_url: bool = False):
        data = io.BytesIO(file_obj.read())

        content_type, _ = mimetypes.guess_type(filename)
        if not content_type or content_type == 'application/octet-stream':
            content_type = 'image/jpeg'

        return self.upload(bucket, filename, data, content_type, return_url)

    def download_file(self, bucket: str, filename: str):
        try:
            return self.client.get_object(bucket, filename)
        except InvalidResponseError as err:
            logger.error(f"Minio download error: {err}")
            return None

    def delete_file(self, bucket: str, filename: str):
        try:
            self.client.remove_object(bucket, filename)
        except InvalidResponseError as err:
            logger.error(f"Minio delete error: {err}")
            return None

    def delete_file_by_url(self, url: str):
        try:
            parsed_url = urlparse(url)
            url_path = parsed_url.path.strip("/")
            parts = url_path.split("/")
            bucket = parts[1]
            filename = "/".join(parts[2:])
            self.client.remove_object(bucket, filename)
        except InvalidResponseError as err:
            logger.error(f"Minio delete error: {err}")
            return None

    def put_b64image(self, bucket, filename, b64_image):
        try:
            imgdata = base64.b64decode(b64_image)
            img_as_stream = io.BytesIO(imgdata)
            self.client.put_object(bucket, filename, img_as_stream, len(imgdata))
            return os.path.join(self.domain, bucket, filename)
        except InvalidResponseError as err:
            logger.error(f"Minio upload error: {err}")
            return None

    def copy_image(self, bucket, image_url, new_filename):
        try:
            response = requests.get(image_url, verify=False)
            self.client.put_object(bucket, new_filename, io.BytesIO(response.content), len(response.content))
            return os.path.join(self.domain, bucket, new_filename)
        except Exception as e:
            logger.error(f"Copy minio failed: {e}")
            return None

    def upload_chunk_file(self, bucket: str, file_path, obj_name: str):
        try:
            self.client.fput_object(bucket_name=bucket, file_path=file_path, object_name=obj_name, part_size=5 * 1024 * 1024)
            return os.path.join(self.domain, bucket, obj_name)
        except Exception as e:
            logger.error(f"Minio upload failed: {e}")
