from rest_framework import mixins

from comic_be.apps.comic.serializers import (
    AuthorSerializers, AuthorCreateSerializer, AuthorUpdateSerializer, serializers
)
from comic_be.apps.comic.views_container import (
    swagger_auto_schema, openapi, permission_crud_comic, CsrfExemptSessionAuthentication, SessionAuthentication,
    LimitOffsetPagination, GenericViewSet, MultiPartParser, FormParser, Author, AppStatus, Response
)


class AuthorViewSet(GenericViewSet, mixins.CreateModelMixin,
                   mixins.ListModelMixin, mixins.UpdateModelMixin):
    queryset = Author.objects.all()
    # permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = LimitOffsetPagination
    authentication_classes = [CsrfExemptSessionAuthentication, SessionAuthentication]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AuthorCreateSerializer
        if self.request.method == 'PUT':
            return AuthorUpdateSerializer
        return AuthorSerializers

    def get_queryset(self):
        name = self.request.query_params.get("name", None)
        queryset = Author.objects.filter().all()
        if name:
            queryset = queryset.filter(name__icontains=name)

        queryset = queryset.order_by("-created_at")
        return queryset

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(name="name", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)]
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)

    def get_object(self):
        author_id = self.kwargs['pk']
        author = Author.objects.filter(id=author_id).first()
        if not author:
            raise serializers.ValidationError(AppStatus.ID_INVALID.message)
        return author

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


