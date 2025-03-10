from comic_be.apps.comic.models_container import (models)
from comic_be.apps.comic.models import Comic


class Chapter(models.Model):
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE)

    number = models.IntegerField(null=False, blank=True)
    title = models.CharField(max_length=255, null=True, blank=False)
    views = models.IntegerField(default=0, blank=False)
    src_image = models.CharField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
