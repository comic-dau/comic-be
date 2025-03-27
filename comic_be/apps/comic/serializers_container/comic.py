from comic_be.apps.comic.serializers_container import (
    Comic, Chapter, serializers, permission_crud_comic, AppStatus, MinioStorage, settings,
    check_validate_genres, create_preview_image, timezone
)


class ComicSerializers(serializers.ModelSerializer):
    last_chapter = serializers.SerializerMethodField()
    author_info = serializers.SerializerMethodField()

    class Meta:
        model = Comic
        exclude = ['author']

    @staticmethod
    def get_last_chapter(obj):
        list_chapters = Chapter.objects.filter(comic=obj.id).order_by('-id')
        if list_chapters:
            last_chapter = list_chapters[0]
            return last_chapter.number
        return None

    @staticmethod
    def get_author_info(obj):
        return {'id': obj.author.id, 'name': obj.author.name}


class ComicBaseSerializer(serializers.ModelSerializer):
    image_upload = serializers.ImageField(required=True, allow_null=False, write_only=True)
    background_image_upload = serializers.ImageField(required=True, allow_null=False, write_only=True)
    image = serializers.CharField(read_only=True)
    background_image = serializers.CharField(read_only=True)
    preview_image = serializers.CharField(read_only=True)


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
        fields = ['name', 'author', 'introduction', 'genres', 'image', 'background_image', 'image_upload',
                  'preview_image', 'background_image_upload']


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

        image_upload = validated_data.pop('image_upload')
        validated_data['image'] = self.handel_image(image_upload, validated_data['name'])

        image_preview = create_preview_image(image_upload)
        validated_data['preview_image'] = self.handel_image(image_preview, validated_data['name'])

        background_image_upload = validated_data.pop('background_image_upload')
        validated_data['background_image'] = self.handel_image(background_image_upload, validated_data['name'])

        comic = Comic.objects.create(**validated_data, updated_at=timezone.now())
        return comic


class ComicUpdateSerializer(ComicBaseSerializer):
    image_upload = serializers.ImageField(required=False, allow_null=True, write_only=True)
    background_image_upload = serializers.ImageField(required=False, allow_null=True, write_only=True)

    def handle_update_image(self, old_url_image, image, name_comic):
        try:
            if old_url_image:
                self.minio_cli.delete_file_by_url(old_url_image)
            file_path = f'comic/{name_comic}/{image.name}'
            uri = self.minio_cli.upload_file(self.bucket, file_path, image, return_url=True)
            return uri
        except Exception as e:
            raise serializers.ValidationError(f"Error uploading image: {str(e)}")

    @staticmethod
    def update_genres(instance, genres):
        current_genres_list = [x.strip() for x in instance.genres.split(",")]
        genres_list = [x.strip() for x in genres.split(",")]
        combined_set_genres = set(current_genres_list) | set(genres_list)
        return ",".join(combined_set_genres)

    @staticmethod
    def _check_permission(user):
        permission_crud_comic(user)

    @staticmethod
    def _validate_name(instance, validated_data):
        name = validated_data.setdefault('name', instance.name)
        if name != instance.name:
            comic_exist = Comic.objects.filter(name=name).first()
            if comic_exist:
                raise serializers.ValidationError(AppStatus.COMIC_NAME_ALREADY_EXIST.message)
        return name

    def _handle_image_field(self, validated_data, field_name, old_field_value, name_comic, is_preview=False):
        image = validated_data.pop(field_name, None)
        if image:
            if is_preview:
                image = create_preview_image(image)
            return self.handle_update_image(old_field_value, image, name_comic)
        return None

    def _handle_image_upload(self, instance, validated_data, name_comic):
        if 'image_upload' in validated_data:
            validated_data['image'] = self._handle_image_field(
                validated_data, 'image_upload', instance.image, name_comic
            )
            validated_data['preview_image'] = self._handle_image_field(
                 validated_data, 'image_upload', instance.preview_image, name_comic, is_preview=True
            )
        if 'background_image_upload' in validated_data:
            validated_data['background_image'] = self._handle_image_field(
                validated_data, 'background_image_upload', instance.background_image, name_comic
            )
        return validated_data

    def process_validated_data(self, instance, validated_data):
        self._check_permission(self.context['request'].user)
        name_comic = self._validate_name(instance, validated_data)

        genres = validated_data.pop('genres', None)
        if genres:
            validated_data['genres'] = self.update_genres(instance, genres)

        validated_data = self._handle_image_upload(instance, validated_data, name_comic)

        for field, value in validated_data.items():
            setattr(instance, field, value)
        return instance

    def update(self, instance, validated_data):
        instance = self.process_validated_data(instance, validated_data)
        instance.save()
        return instance


class ComicChapterSerializer(serializers.ModelSerializer):
    list_chapters = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Comic
        fields = ['name', 'author', 'introduction', 'genres', 'image', 'list_chapters']
