from comic_be.apps.comic.serializers_container import (
    History, serializers
)


class HistorySerializers(serializers.ModelSerializer):
    comic_info = serializers.SerializerMethodField()
    chapter_info = serializers.SerializerMethodField()

    class Meta:
        model = History
        exclude = ['comic', 'chapter']


    @staticmethod
    def get_comic_info(obj):
        return {'id': obj.comic.id, 'name': obj.comic.name}

    @staticmethod
    def get_chapter_info(obj):
        return {'id': obj.chapter.id, 'number': obj.chapter.number, 'title': obj.chapter.title}
