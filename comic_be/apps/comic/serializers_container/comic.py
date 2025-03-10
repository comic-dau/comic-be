from comic_be.apps.comic.serializers_container import (
    Comic, serializers, permission_crud_comic, AppStatus, MinioStorage, settings,
    check_validate_genres
)


class ComicSerializers(serializers.ModelSerializer):
    class Meta:
        model = Comic
        fields = '__all__'


class ComicBaseSerializer(serializers.ModelSerializer):
    image_avatar = serializers.ImageField(required=True, allow_null=False, write_only=True)
    image = serializers.CharField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.minio_cli = MinioStorage()
        self.bucket = settings.STORAGE_BUCKET

    @staticmethod
    def validate_genres(genres):
        check_validate_genres(genres)
        return genres

    class Meta:
        model = Comic
        fields = ['name', 'author', 'introduction', 'genres', 'image', 'image_avatar']


class ComicCreateSerializer(ComicBaseSerializer):
    def handel_image(self, image, name_comic):
        file_path = f'comic/{name_comic}/{image.name}'
        uri = self.minio_cli.upload_file(self.bucket, file_path, image, return_url=True)
        return uri

    def create(self, validated_data):
        current_user = self.context['request'].user
        permission_crud_comic(current_user)

        comic_exist = Comic.objects.filter(name=validated_data['name']).first()
        if comic_exist:
            raise serializers.ValidationError(AppStatus.COMIC_ALREADY_EXIST.message)

        image_avatar = validated_data.pop('image_avatar')
        validated_data['image'] = self.handel_image(image_avatar, validated_data['name'])

        comic = Comic.objects.create(**validated_data)
        return comic


class ComicUpdateSerializer(ComicBaseSerializer):
    image_avatar = serializers.ImageField(required=False, allow_null=True, write_only=True)

    def handel_update_image(self, old_url_image, image, name_comic):
        self.minio_cli.delete_file_by_url(old_url_image)
        file_path = f'comic/{name_comic}/{image.name}'
        uri = self.minio_cli.upload_file(self.bucket, file_path, image, return_url=True)
        return uri

    @staticmethod
    def provider_genres(instance, genres):
        current_genres = instance.genres
        current_genres_list = [x.strip() for x in current_genres.split(",")]
        genres_list = [x.strip() for x in genres.split(",")]
        combined_set_genres = set(current_genres_list) | set(genres_list)
        result_genres = ",".join(combined_set_genres)
        return result_genres

    def provider_validated_data(self, instance, validated_data):
        current_user = self.context['request'].user
        permission_crud_comic(current_user)
        name_comic = instance.name

        if validated_data.get('name', None):
            comic_exist = Comic.objects.filter(name=validated_data['name']).first()
            if comic_exist:
                raise serializers.ValidationError(AppStatus.COMIC_NAME_ALREADY_EXIST.message)
            name_comic = validated_data.get('name')

        genres = validated_data.pop('genres', None)
        if genres:
            validated_data['genres'] = self.provider_genres(instance, genres)

        image_avatar = validated_data.pop('image_avatar', None)
        if image_avatar:
            validated_data['image'] = self.handel_update_image(instance.image, image_avatar, name_comic)

        for field, value in validated_data.items():
            setattr(instance, field, value)
        return instance

    def update(self, instance, validated_data):
        instance = self.provider_validated_data(instance, validated_data)
        instance.save()
        return instance
