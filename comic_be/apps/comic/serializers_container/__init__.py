import random
import zipfile
from datetime import timedelta

from os.path import join
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework import serializers
from django.utils.html import strip_tags
from rest_framework.response import Response
from django.core.files.base import ContentFile

# from namanga.setting.path import cfg
from comic_be.apps.comic.models import *
# from namanga.apps.engine.utils.helper import *
from comic_be.apps.comic.utils.constants import AppStatus
from comic_be.apps.comic.utils.permission import permission_crud_comic
from comic_be.apps.comic.models_container.enum_type import ComicGenreEnum
from comic_be.apps.core.minio_cli import MinioStorage
from comic_be.apps.comic.utils.valid_data import check_validate_genres
from comic_be.apps.comic.utils.preview_image import create_preview_image
