from comic_be.apps.comic.serializers_container import (
    Author, serializers, permission_crud_comic, AppStatus, MinioStorage, settings
)


class AuthorSerializers(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class AuthorBaseSerializer(serializers.ModelSerializer):
    image_avatar = serializers.ImageField(required=True, allow_null=False, write_only=True)
    image = serializers.CharField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.minio_cli = MinioStorage()
        self.bucket = settings.STORAGE_BUCKET

    class Meta:
        model = Author
        fields = ['name', 'des', 'image', 'image_avatar']


class AuthorCreateSerializer(AuthorBaseSerializer):
    def handel_image(self, image, name_author):
        file_path = f'author/{name_author}/{image.name}'
        uri = self.minio_cli.upload_file(settings.STORAGE_BUCKET, file_path, image, return_url=True)
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


class AuthorUpdateSerializer(AuthorBaseSerializer):
    image_avatar = serializers.ImageField(required=False, allow_null=True, write_only=True)

    def handel_update_image(self, old_url_image, image, name_author):
        self.minio_cli.delete_file_by_url(old_url_image)
        file_path = f'author/{name_author}/{image.name}'
        uri = self.minio_cli.upload_file(self.bucket, file_path, image, return_url=True)
        return uri

    def provider_validated_data(self, instance, validated_data):
        name_author = instance.name
        if validated_data.get('name', None):
            author_exist = Author.objects.filter(name=validated_data['name']).first()
            if author_exist:
                raise serializers.ValidationError(AppStatus.AUTHOR_NAME_ALREADY_EXIST.message)
            name_author = validated_data.get('name')

        image_avatar = validated_data.pop('image_avatar', None)
        if image_avatar:
            validated_data['image'] = self.handel_update_image(instance.image, image_avatar, name_author)

        for field, value in validated_data.items():
            setattr(instance, field, value)
        return instance

    def update(self, instance, validated_data):
        instance = self.provider_validated_data(instance, validated_data)
        instance.save()
        return instance
