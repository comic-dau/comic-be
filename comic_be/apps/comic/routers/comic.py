from rest_framework import routers
from comic_be.apps.comic.routers import *
from comic_be.apps.comic.views import (ComicViewSet)

router = routers.DefaultRouter(trailing_slash=False)
router.register('', ComicViewSet)

urlpatterns = [
    path("", include(router.urls)),
]