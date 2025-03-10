from comic_be.apps.comic.models_container import (models)
from comic_be.apps.comic.models_container.author import Author


class Comic(models.Model):
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.CASCADE)

    name = models.CharField(max_length=255, null=True, blank=True)
    genres = models.TextField(null=True, blank=True)
    introduction = models.TextField(null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    views = models.IntegerField(default=0)
    total_chapter = models.IntegerField(null=True, blank=True, default=0)
    like = models.IntegerField(null=True, blank=True, default=0)
    rating = models.IntegerField(null=True, blank=True, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
