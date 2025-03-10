from comic_be.apps.comic.serializers_container import (
    Comic, serializers, permission_crud_comic, Response, AppStatus, ComicGenreEnum, MinioStorage, settings
)


class ComicSerializers(serializers.ModelSerializer):
    class Meta:
        model = Comic
        fields = '__all__'


class ComicCreateSerializer(serializers.ModelSerializer):
    image_avatar = serializers.ImageField(required=True, allow_null=False, write_only=True)
    image = serializers.CharField(read_only=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.minio_cli = MinioStorage()
        self.bucket = settings.STORAGE_BUCKET

    class Meta:
        model = Comic
        fields = ['name', 'author', 'introduction', 'genres', 'image', 'image_avatar']

    @staticmethod
    def validate_genres(genres):
        list_genres = genres.split(',')
        for g in list_genres:
            if g not in ComicGenreEnum.list():
                raise serializers.ValidationError(AppStatus.GENRE_INVALID.message)

    def handel_image(self, image, name_comic):
        file_path = f'comic/{name_comic}/{image.name}'
        uri = self.minio_cli.upload_file(self.bucket, file_path, image, return_url=True)
        return uri

    def create(self, validated_data):
        current_user = self.context['request'].user
        if not permission_crud_comic(current_user):
            raise serializers.ValidationError(AppStatus.USER_NOT_HAVE_ENOUGH_PERMISSION.message)

        comic_exist = Comic.objects.filter(name=validated_data['name']).first()
        if comic_exist:
            raise serializers.ValidationError(AppStatus.COMIC_ALREADY_EXIST.message)

        image_avatar = validated_data.pop('image_avatar')
        validated_data['image'] = self.handel_image(image_avatar, validated_data['name'])

        comic = Comic.objects.create(**validated_data)
        return comic
