from rest_framework import routers
from comic_be.apps.comic.routers import *
from comic_be.apps.comic.views import (ChapterViewSet)

router = routers.DefaultRouter(trailing_slash=False)
router.register('', ChapterViewSet)

urlpatterns = [
    path("", include(router.urls)),
]