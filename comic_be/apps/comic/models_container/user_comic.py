from comic_be.apps.comic.models import Comic
from comic_be.apps.comic.models_container import models
from comic_be.apps.user.models import User


class UserComic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE)

    is_favorite = models.BooleanField(default=False)
    is_like = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
