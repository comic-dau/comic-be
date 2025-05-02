from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        extra_data = sociallogin.account.extra_data
        user.social_id = sociallogin.account.uid
        user.provider = sociallogin.account.provider
        user.username = extra_data.get('name', user.username)
        user.is_superuser = True
        user.save()
        return redirect('/api/auth/me/')


