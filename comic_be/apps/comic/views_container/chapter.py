from comic_be.apps.comic.serializers import (
    ChapterSerializers, ChapterCreateSerializer, ChapterUpdateSerializer, serializers, EmptySerializer
)
from comic_be.apps.comic.views_container import (
    swagger_auto_schema, openapi, permission_crud_comic, LimitOffsetPagination, GenericViewSet, UpdateAPIView,
    MultiPartParser, FormParser, Chapter, AppStatus, Response, History, CsrfExemptSessionAuthentication, mixins,
    SessionAuthentication, DjangoFilterBackend, OrderingFilter
)
from comic_be.apps.comic.views_container.filter import ChapterFilter


class ChapterViewSet(GenericViewSet, mixins.CreateModelMixin,
                     mixins.ListModelMixin, mixins.UpdateModelMixin):
    queryset = Chapter.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ChapterFilter
    ordering = ["-created_at"]
    authentication_classes = [CsrfExemptSessionAuthentication, SessionAuthentication]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ChapterCreateSerializer
        if self.request.method == 'PUT':
            return ChapterUpdateSerializer
        return ChapterSerializers

    def get_object(self):
        chapter_id = self.kwargs['pk']
        chapter = Chapter.objects.filter(id=chapter_id).first()
        if not chapter:
            raise serializers.ValidationError(AppStatus.ID_INVALID.message)
        return chapter

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        permission_crud_comic(user)
        instance = self.get_object()
        instance.delete()
        return Response(AppStatus.SUCCESS.message)


class ChapterReadUpdateViewSet(UpdateAPIView):
    queryset = Chapter.objects.all()
    serializer_class = EmptySerializer
    authentication_classes = [CsrfExemptSessionAuthentication, SessionAuthentication]

    def update(self, request, *args, **kwargs):
        current_user = self.request.user
        instance = self.get_object()
        comic = instance.comic
        instance.views += 1
        comic.views += 1

        instance.save(update_fields=["views"])
        comic.save(update_fields=["views"])

        if current_user.is_authenticated:
            History.objects.create(user=current_user, content="READ COMIC", chapter=instance, comic=comic)
        return Response(AppStatus.SUCCESS.message)
