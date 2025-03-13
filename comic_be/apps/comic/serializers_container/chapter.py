from comic_be.apps.comic.serializers_container import (
    serializers, Chapter, zipfile, ContentFile, settings, permission_crud_comic, timezone
)
from comic_be.apps.core.minio_cli import MinioStorage


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.minio_cli = MinioStorage()

    class Meta:
        model = Chapter
        fields = ['comic', 'number', 'title', 'src_image', 'file_image']

    @staticmethod
    def validate_file_image(value):
        if not value.name.endswith('.zip'):
            raise serializers.ValidationError("File phải có định dạng .zip")
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("File không được lớn hơn 50MB")
        return value

    def provider_src_image(self, zip_file, comic_name, number_chapter):
        image_urls = []
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                image_data = zip_ref.read(file_info.filename)
                # Tạo ContentFile từ dữ liệu ảnh
                image_file = ContentFile(image_data, name=file_info.filename)

                # Upload lên Minio và lấy URL
                file_path = f"comic/{comic_name}/chap_{number_chapter}/{file_info.filename}"
                uri = self.minio_cli.upload_file(
                    bucket=settings.STORAGE_BUCKET,
                    filename=file_path,
                    file_obj=image_file,
                    return_url=True
                )
                image_urls.append(uri)
        return image_urls

    def create(self, validated_data):
        current_user = self.context['request'].user
        permission_crud_comic(current_user)
        comic = validated_data.get('comic', None)
        number_chapter = validated_data.get('number', None)
        if not number_chapter:
            raise serializers.ValidationError("Require number chapter.")

        zip_file = validated_data.pop('file_image')
        validated_data['src_image'] = self.provider_src_image(zip_file, comic.name, number_chapter)

        chapter = Chapter.objects.create(**validated_data)
        comic.update_at = timezone.now()
        comic.save()
        return chapter


class ChapterUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['number', 'title']

    def update(self, instance, validated_data):
        current_user = self.context['request'].user
        permission_crud_comic(current_user)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
