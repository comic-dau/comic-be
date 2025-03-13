from comic_be.apps.comic.models_container import models
from comic_be.apps.comic.models_container.chapter import Chapter
from comic_be.apps.comic.models_container.comic import Comic
from comic_be.apps.user.models import User


class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE)

    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
