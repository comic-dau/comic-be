from comic_be.apps.comic.serializers_container import (
    Author, serializers, permission_crud_comic, AppStatus, MinioStorage, settings
)


class AuthorSerializers(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class AuthorCreateSerializer(serializers.ModelSerializer):
    image_avatar = serializers.ImageField(required=True, allow_null=False, write_only=True)
    image = serializers.CharField(read_only=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.minio_cli = MinioStorage()
        self.bucket = settings.STORAGE_BUCKET

    class Meta:
        model = Author
        fields = ['name', 'des', 'image', 'image_avatar']

    def handel_image(self, image, name_author):
        file_path = f'author/{name_author}/{image.name}'
        uri = self.minio_cli.upload_file(self.bucket, file_path, image, return_url=True)
        return uri

    def create(self, validated_data):
        current_user = self.context['request'].user
        permission_crud_comic(current_user)

        author_exist = Author.objects.filter(name=validated_data['name']).first()
        if author_exist:
            raise serializers.ValidationError(AppStatus.COMIC_ALREADY_EXIST.message)

        image_avatar = validated_data.pop('image_avatar')
        validated_data['image'] = self.handel_image(image_avatar, validated_data['name'])

        author = Author.objects.create(**validated_data)
        return author
