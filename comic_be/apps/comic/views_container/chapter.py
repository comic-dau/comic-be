from rest_framework import mixins
from rest_framework.generics import UpdateAPIView

from comic_be.apps.comic.serializers import (
    ChapterSerializers, ChapterCreateSerializer, ChapterUpdateSerializer, serializers,
)
from comic_be.apps.comic.views_container import (
    swagger_auto_schema, openapi, permission_crud_comic, LimitOffsetPagination, GenericViewSet,
    MultiPartParser, FormParser, Chapter, AppStatus, Response, History, Comic
)


class ChapterViewSet(GenericViewSet, mixins.CreateModelMixin,
                     mixins.ListModelMixin, mixins.UpdateModelMixin):
    queryset = Chapter.objects.all()
    # permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ChapterCreateSerializer
        if self.request.method == 'PUT':
            return ChapterUpdateSerializer
        return ChapterSerializers

    def get_queryset(self):
        comic = self.request.query_params.get("comic", None)
        queryset = Chapter.objects.filter().all()
        if comic:
            queryset = queryset.filter(comic=comic)
            if not queryset:
                raise serializers.ValidationError(AppStatus.ID_INVALID.message)

        queryset = queryset.order_by("-created_at")
        return queryset

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(name="comic", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER), ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)

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
    serializer_class = None

    def update(self, request, *args, **kwargs):
        current_user = self.request.user
        instance = self.get_object()
        comic = instance.comic
        instance.views += 1
        comic.views += 1

        instance.save(update_fields=["views"])
        comic.save(update_fields=["views"])

        if current_user.is_authenticated:
            History.objects.create(user=current_user, chapter=instance, comic=comic)
        return Response(AppStatus.SUCCESS.message)
