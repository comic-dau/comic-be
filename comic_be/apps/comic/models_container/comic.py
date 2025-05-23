from comic_be.apps.comic.models_container import (models)
from comic_be.apps.comic.models_container.author import Author


class Comic(models.Model):
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.CASCADE)

    name = models.CharField(max_length=255, null=True, blank=True)
    genres = models.TextField(null=True, blank=True)
    introduction = models.TextField(null=True, blank=True)
    background_image = models.CharField(null=True, blank=True)
    image = models.CharField(null=True, blank=True)
    preview_image = models.CharField(null=True, blank=True)
    views = models.IntegerField(default=0)
    total_chapter = models.IntegerField(null=True, blank=True, default=0)
    reviews = models.JSONField(default={'likes': 0, 'rating': 0, 'number_of_user_rating': 0})

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField()
