from comic_be.apps.comic.views_container import (
    filters, UserComic, Comic, check_validate_genres, Chapter
)


class ComicFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    author = filters.CharFilter(field_name="author__name", lookup_expr="icontains")
    genres = filters.CharFilter(method="filter_genres")

    class Meta:
        model = Comic
        fields = ["name", "author", "genres"]

    @staticmethod
    def filter_genres(queryset, name, value):
        check_validate_genres(value)
        return queryset.filter(genres__contains=value)


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
