from comic_be.apps.comic.routers import *

urlpatterns = [
    path('comic/', include('comic_be.apps.comic.routers.comic')),
    path('author/', include('comic_be.apps.comic.routers.author')),
]
