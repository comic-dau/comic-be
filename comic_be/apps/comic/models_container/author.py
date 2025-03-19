from comic_be.apps.comic.models_container import (models)


class Author(models.Model):
    name = models.CharField(null=False, blank=True)
    des = models.TextField(null=True, blank=False)
    image = models.CharField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
