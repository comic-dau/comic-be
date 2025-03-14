from django.urls import path
from . import views

urlpatterns = [
    path('auth/google/', views.GoogleLoginAPI.as_view(), name='google_login'),
    path('auth/facebook/', views.FacebookLoginAPI.as_view(), name='facebook_login'),
    path('auth/logout/', views.LogoutAPIView.as_view(), name='facebook_login'),
    path('auth/first_login/', views.FirstLoginAPIView.as_view(), name='social_callback'),
    path('auth/cookies/', views.CookiesAPIView.as_view(), name='social_callback'),
    path('auth/me/', views.GetMeAPIView.as_view(), name='social_callback'),
]