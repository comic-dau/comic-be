from rest_framework.authentication import SessionAuthentication

from comic_be.apps.comic.views_container import (
    permission_crud_comic, LimitOffsetPagination, GenericViewSet, MultiPartParser,
    FormParser, UserComic, AppStatus, Response, mixins, OrderingFilter, DjangoFilterBackend,
    CsrfExemptSessionAuthentication
)
from comic_be.apps.user.serializers_container.user_comic import (
    # UserComicSerializers, UserComicCreateSerializer, UserComicUpdateSerializer,
    UserComicSerializers, serializers, UserComicCreateSerializer
)
from comic_be.apps.comic.views_container.filter import UserComicFilter


class UserComicViewSet(GenericViewSet, mixins.CreateModelMixin,
                       mixins.ListModelMixin, mixins.UpdateModelMixin):
    queryset = UserComic.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = UserComicFilter
    ordering_fields = ['-comic_id']
    ordering = ['-comic_id']
    authentication_classes = [CsrfExemptSessionAuthentication, SessionAuthentication]

    def get_serializer_class(self):
            if self.request.method == 'POST':
                return UserComicCreateSerializer
            return UserComicSerializers

    def get_object(self):
        comic_id = self.kwargs['pk']
        comic = UserComic.objects.filter(id=comic_id).first()
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
