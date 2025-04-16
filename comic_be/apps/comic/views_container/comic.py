from comic_be.apps.comic.serializers import (
    ComicSerializers, ComicCreateSerializer, ComicUpdateSerializer, serializers,
)
from comic_be.apps.comic.views_container import (
    permission_crud_comic, LimitOffsetPagination, GenericViewSet, MultiPartParser, FormParser, Comic, AppStatus,
    Response, mixins, DjangoFilterBackend, OrderingFilter, CsrfExemptSessionAuthentication, SessionAuthentication
)
from comic_be.apps.comic.views_container.filter import ComicFilter


class ComicViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin):
    queryset = Comic.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ComicFilter
    ordering_fields = ["name", "updated_at"]
    ordering = ["-updated_at"]
    authentication_classes = [CsrfExemptSessionAuthentication, SessionAuthentication]


    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ComicCreateSerializer
        if self.request.method == 'PUT':
            return ComicUpdateSerializer
        return ComicSerializers

    def get_object(self):
        comic_id = self.kwargs['pk']
        comic = Comic.objects.filter(id=comic_id).first()
        if not comic:
            raise serializers.ValidationError(AppStatus.ID_INVALID.message)
        return comic

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

