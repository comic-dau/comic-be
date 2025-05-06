from comic_be.apps.comic.views_container import (
    LimitOffsetPagination, GenericViewSet,
    MultiPartParser, FormParser, History, AppStatus, Response, mixins, permissions, CsrfExemptSessionAuthentication,
    SessionAuthentication
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
    authentication_classes = [CsrfExemptSessionAuthentication, SessionAuthentication]

    def get_serializer_class(self):
        return HistorySerializers

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return History.objects.none()

        queryset = History.objects.filter().all()
        queryset = queryset.filter(user=user)
        queryset = queryset.order_by("-created_at")
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        user = request.user

        # Get filter parameters from form data instead of query parameters
        comic = request.data.get("comic", None)
        chapter = request.data.get("chapter", None)

        if comic:
            queryset = queryset.filter(comic=comic)
        if chapter:
            queryset = queryset.filter(chapter=chapter)
        if user.is_superuser:
            user_query = request.data.get("user", None)
            if user_query:
                queryset = queryset.filter(user=user_query)

        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
