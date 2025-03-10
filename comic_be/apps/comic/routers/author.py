from rest_framework import routers
from comic_be.apps.comic.routers import *
from comic_be.apps.comic.views import (AuthorViewSet)

router = routers.DefaultRouter(trailing_slash=False)
router.register('', AuthorViewSet)

urlpatterns = [
    path("", include(router.urls)),
]