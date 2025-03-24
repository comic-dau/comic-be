from rest_framework import serializers
from comic_be.apps.comic.utils.constants import AppStatus


def permission_user(user):
    if not user.is_authenticated or user.is_anonymous:
        raise serializers.ValidationError(AppStatus.AUTHENTICATION_FAILED.message)


def permission_crud_comic(user):
    permission_user(user)
    if user.email != 'vietgym007@gmail.com' and not user.is_superuser:
        raise serializers.ValidationError(AppStatus.USER_NOT_HAVE_ENOUGH_PERMISSION.message)
