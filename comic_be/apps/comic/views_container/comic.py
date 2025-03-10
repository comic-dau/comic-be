from rest_framework import mixins

from comic_be.apps.comic.serializers import (
    ComicSerializers, ComicCreateSerializer, serializers, Response
)
from comic_be.apps.comic.views_container import (
    permissions, swagger_auto_schema, openapi, permission_crud_comic, permission_user,
    LimitOffsetPagination, GenericViewSet,
    MultiPartParser, FormParser, Comic, AppStatus
)


class ComicViewSet(GenericViewSet, mixins.CreateModelMixin,
                   mixins.ListModelMixin, mixins.UpdateModelMixin):
    queryset = Comic.objects.all()
    # permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ComicCreateSerializer
        return ComicSerializers

    def get_queryset(self):
        name = self.request.query_params.get("name", None)
        author = self.request.query_params.get("author", None)
        queryset = Comic.objects.filter().all()
        if name:
            queryset = queryset.filter(name__icontains=name)

        if author:
            queryset = queryset.filter(author__icontains=author)
        queryset = queryset.order_by("-created_at")
        return queryset

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(name="name", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter(name="author", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING), ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)

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


