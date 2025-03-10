from rest_framework import serializers

from comic_be.apps.comic.models_container import ComicGenreEnum
from comic_be.apps.comic.utils.constants import AppStatus


def check_validate_genres(genres):
    list_genres = genres.split(',')
    for g in list_genres:
        if g not in ComicGenreEnum.list():
            raise serializers.ValidationError(AppStatus.GENRE_INVALID.message)

