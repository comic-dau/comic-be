from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.response import Response
from rest_framework.views import APIView

from comic_be import settings
from comic_be.apps.user.serializers_container.auth_socials import (
    SocialUserSerializer, LogoutSerializer, RedirectSerializer, CookiesSerializer
)


class GoogleLoginAPI(APIView):
    def get(self, request):
        # google_auth_url = f"{request.scheme}://{request.get_host()}/accounts/google/login/?next={settings.FE_URL}"
        google_auth_url = f"{request.scheme}://{request.get_host()}/accounts/google/login/?next=/api/auth/first_login/"
        return redirect(google_auth_url)


class FacebookLoginAPI(APIView):
    def get(self, request):
        facebook_auth_url = f"{request.scheme}://{request.get_host()}/accounts/facebook/login/?next={settings.FE_URL}"
        return redirect(facebook_auth_url)


class LogoutAPIView(APIView):
    def get(self, request, *args, **kwargs):
        serializer = LogoutSerializer(data={}, context={'request': request})
        if serializer.is_valid():
            redirect_url = serializer.get_redirect_url()
            return redirect(redirect_url)
        return Response({"error": serializer.errors}, status=400)


@method_decorator(ensure_csrf_cookie, name='get')
class FirstLoginAPIView(APIView):
    def get(self, request):
        serializer = RedirectSerializer(context={'request': request})
        redirect_url = serializer.get_redirect_url()  # Gọi hàm lấy redirect_url
        return redirect(redirect_url)


@method_decorator(ensure_csrf_cookie, name='get')
class CookiesAPIView(APIView):
    def get(self, request):
        serializer = CookiesSerializer(data={}, context={'request': request})
        if serializer.is_valid():
            return Response(serializer.get_cookies(), status=200)
        return Response({'error': serializer.errors}, status=400)


class GetMeAPIView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            serializer = SocialUserSerializer(request.user)
            return Response(serializer.data)
        return Response({'error': 'Authentication failed'}, status=400)
