import os
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.parsers import MultiPartParser, FormParser

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import mixins
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import UpdateAPIView
from rest_framework.generics import GenericAPIView, RetrieveAPIView, ListAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from comic_be.apps.user.models import User
from comic_be.apps.comic.models import Comic
from comic_be.apps.comic.models import Author
from comic_be.apps.comic.models import Chapter
from comic_be.apps.comic.models import History
from comic_be.apps.comic.utils.constants import AppStatus
from comic_be.apps.comic.utils.valid_data import check_validate_genres
from comic_be.apps.comic.utils.permission import permission_crud_comic, permission_user


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return
