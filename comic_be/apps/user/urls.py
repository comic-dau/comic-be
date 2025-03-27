from django.urls import path, include
from rest_framework import routers

from . import views
from ..user.views_container.history import HistoryViewSet
from ..user.views_container.user_comic import UserComicViewSet

router_history = routers.DefaultRouter(trailing_slash=False)
router_history.register('', HistoryViewSet)

router_user_comic = routers.DefaultRouter(trailing_slash=False)
router_user_comic.register('', UserComicViewSet)


urlpatterns = [
    path('auth/google/', views.GoogleLoginAPI.as_view(), name='google_login'),
    path('auth/facebook/', views.FacebookLoginAPI.as_view(), name='facebook_login'),
    path('auth/logout/', views.LogoutAPIView.as_view(), name='facebook_login'),
    path('auth/first_login/', views.FirstLoginAPIView.as_view(), name='social_callback'),
    path('auth/cookies/', views.CookiesAPIView.as_view(), name='social_callback'),
    path('auth/me/', views.GetMeAPIView.as_view(), name='social_callback'),
    path("history/", include(router_history.urls)),
    path("user_comic/", include(router_user_comic.urls)),
]