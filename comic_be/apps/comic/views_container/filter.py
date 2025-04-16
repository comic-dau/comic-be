from rest_framework import serializers

from comic_be.apps.comic.views_container import (
    filters, UserComic, Comic, check_validate_genres, Chapter
)


class ComicFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    author = filters.CharFilter(field_name="author__name", lookup_expr="icontains")
    genres = filters.CharFilter(method="filter_genres")
    is_favorite = filters.BooleanFilter(method="filter_favorite")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.get('request', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Comic
        fields = ["name", "author", "genres", "is_favorite"]

    @staticmethod
    def filter_genres(queryset, name, value):
        check_validate_genres(value)
        return queryset.filter(genres__contains=value)

    def filter_favorite(self, queryset, name, value, **kwargs):
        if value is True:
            if hasattr(self, 'request') and self.request and getattr(self.request, 'user',
                                                                     None) and self.request.user.is_authenticated:
                favorite_comic_ids = UserComic.objects.filter(
                    user=self.request.user,
                    is_favorite=True
                ).values_list('comic_id', flat=True)
                return queryset.filter(id__in=favorite_comic_ids)
            else:
                raise serializers.ValidationError("Authentication failed.")
        return queryset


class UserComicFilter(filters.FilterSet):
    comic = filters.BaseInFilter(field_name="comic", lookup_expr="in")

    class Meta:
        model = UserComic
        fields = ['comic']


class ChapterFilter(filters.FilterSet):
    comic = filters.BaseInFilter(field_name="comic")

    class Meta:
        model = Chapter
        fields = ["comic"]
