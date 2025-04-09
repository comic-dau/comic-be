from comic_be.apps.comic.views_container import (
    filters, UserComic, Comic, check_validate_genres, Chapter
)


class ComicFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    author = filters.CharFilter(field_name="author__name", lookup_expr="icontains")
    genres = filters.CharFilter(method="filter_genres")
    is_favorite = filters.BooleanFilter(method="filter_favorite")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Comic
        fields = ["name", "author", "genres", "is_favorite"]

    @staticmethod
    def filter_genres(queryset, name, value):
        check_validate_genres(value)
        return queryset.filter(genres__contains=value)

    def filter_favorite(self, queryset, name, value):
        # Chỉ xử lý khi value là True
        if value is True and self.request and hasattr(self.request, 'user') and self.request.user.is_authenticated:
            # Lấy danh sách comic_id mà user hiện tại đã đánh dấu là yêu thích
            favorite_comic_ids = UserComic.objects.filter(
                user=self.request.user,
                is_favorite=True
            ).values_list('comic_id', flat=True)

            # Lọc queryset chỉ lấy những comic có trong danh sách yêu thích
            return queryset.filter(id__in=favorite_comic_ids)
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
