from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from rest_framework import serializers

from comic_be import settings

User = get_user_model()


class CookiesSerializer(serializers.Serializer):
    def get_cookies(self):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return f'csrftoken={request.COOKIES.get("csrftoken")}; sessionid={request.COOKIES.get("sessionid")}'
        raise serializers.ValidationError("Authentication failed")


class RedirectSerializer(serializers.Serializer):
    def get_redirect_url(self):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return f"{settings.FE_URL}"
        raise serializers.ValidationError("Authentication failed")


class LogoutSerializer(serializers.Serializer):
    def get_redirect_url(self,):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return f"/accounts/logout/?next={settings.FE_URL}"
        raise serializers.ValidationError("No user is logged in")


class SocialUserSerializer(serializers.ModelSerializer):
    social_id = serializers.CharField(source='socialaccount.uid', read_only=True)
    provider = serializers.CharField(source='socialaccount.provider', read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'social_id', 'provider', 'avatar', 'is_superuser']

    def get_avatar(self, obj):
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not hasattr(instance, 'socialaccount'):
            social_account = SocialAccount.objects.filter(user=instance).first()
            if social_account:
                representation['social_id'] = social_account.uid
                representation['provider'] = social_account.provider
                representation['avatar'] = social_account.get_avatar_url()
        return representation
