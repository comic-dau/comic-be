from comic_be.apps.comic.serializers_container import (
    serializers, Chapter, zipfile, ContentFile, settings, permission_crud_comic, timezone, split_and_shuffle_image,
)
from comic_be.apps.core.minio_cli import MinioStorage


def provider_src_image(minio_cli, zip_file, comic_name, number_chapter):
    image_urls = []
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            image_data = zip_ref.read(file_info.filename)
            # Tạo ContentFile từ dữ liệu ảnh
            image_file = ContentFile(image_data, name=file_info.filename)

            image_file = split_and_shuffle_image(image_file, settings.KEY_HASH_IMG)

            # Upload lên Minio và lấy URL
            file_path = f"comic/{comic_name}/chap_{number_chapter}/{file_info.filename}"
            uri = minio_cli.upload_file(
                bucket=settings.STORAGE_BUCKET,
                filename=file_path,
                file_obj=image_file,
                return_url=True
            )
            image_urls.append(uri)
    return image_urls


class ChapterSerializers(serializers.ModelSerializer):
    comic_info = serializers.SerializerMethodField()
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()

    class Meta:
        model = Chapter
        fields = ['id', 'comic_info', 'number', 'title', 'views', 'src_image', 'updated_at', 'created_at']

    @staticmethod
    def get_comic_info(obj):
        comic = obj.comic
        comic_info = {
            'id': comic.id,
            'name': comic.name
        }
        return comic_info


class ChapterCreateSerializer(serializers.ModelSerializer):
    file_image = serializers.FileField(required=True, write_only=True)
    src_image = serializers.CharField(read_only=True)
    title = serializers.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.minio_cli = MinioStorage()

    class Meta:
        model = Chapter
        fields = ['comic', 'title', 'src_image', 'file_image']

    @staticmethod
    def validate_file_image(value):
        if not value.name.endswith('.zip'):
            raise serializers.ValidationError("File phải có định dạng .zip")
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("File không được lớn hơn 50MB")
        return value

    def create(self, validated_data):
        current_user = self.context['request'].user
        permission_crud_comic(current_user)
        comic = validated_data.get('comic', None)

        validated_data['number'] = comic.total_chapter + 1
        if not validated_data.get('title', None):
            validated_data['title'] = f"Chapter {validated_data['number']}"
        else:
            validated_data['title'] = f"Chapter {validated_data['number']}: " + validated_data['title']

        zip_file = validated_data.pop('file_image')
        validated_data['src_image'] = provider_src_image(self.minio_cli, zip_file, comic.name, validated_data['number'])

        chapter = Chapter.objects.create(**validated_data)

        comic.total_chapter += 1
        comic.updated_at = timezone.now()
        comic.save()
        return chapter


class ChapterUpdateSerializer(serializers.ModelSerializer):
    new_src_image = serializers.FileField(required=False, write_only=True)
    src_image = serializers.CharField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.minio_cli = MinioStorage()

    class Meta:
        model = Chapter
        fields = ['number', 'title', 'new_src_image', 'src_image']

    def handel_update_src_image(self, instance, new_src_image):
        old_src_image = eval(instance.src_image)
        for image in old_src_image:
            self.minio_cli.delete_file_by_url(image)
        src_image = provider_src_image(self.minio_cli, new_src_image, instance.comic.name, instance.number)
        return src_image

    def update(self, instance, validated_data):
        current_user = self.context['request'].user
        permission_crud_comic(current_user)
        if validated_data.get('new_src_image'):
            src_image = validated_data.pop('new_src_image')
            instance.src_image = self.handel_update_src_image(instance, src_image)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
