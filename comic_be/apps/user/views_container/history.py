from comic_be.apps.comic.views_container import (
    swagger_auto_schema, openapi, LimitOffsetPagination, GenericViewSet,
    MultiPartParser, FormParser, History, AppStatus, Response, mixins, permissions
)
from comic_be.apps.user.serializers_container.history import (
    HistorySerializers, serializers
)


class HistoryViewSet(GenericViewSet, mixins.CreateModelMixin,
                     mixins.ListModelMixin, mixins.UpdateModelMixin):
    queryset = History.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        return HistorySerializers

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return History.objects.none()
        comic = self.request.query_params.get("comic", None)
        chapter = self.request.query_params.get("chapter", None)
        queryset = History.objects.filter().all()

        if comic:
            queryset = queryset.filter(comic=comic)
        if chapter:
            queryset = queryset.filter(chapter=chapter)
        if user.is_superuser:
            user_query = self.request.query_params.get("user", None)
            if user_query:
                queryset = queryset.filter(user=user_query)
        else:
            queryset = queryset.filter(user=user)

        queryset = queryset.order_by("-created_at")
        return queryset

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(name="comic", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter(name="chapter", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter(name="users", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER), ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)

    def get_object(self):
        history_id = self.kwargs['pk']
        history = History.objects.filter(id=history_id).first()
        if not history:
            raise serializers.ValidationError(AppStatus.ID_INVALID.message)
        return history

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(AppStatus.SUCCESS.message)
