from django.db import models
from django.contrib.auth.models import AbstractUser
from django.shortcuts import redirect


class User(AbstractUser):
    social_id = models.CharField(max_length=255, blank=True, null=True)
    provider = models.CharField(max_length=50, blank=True, null=True)

# Trong adapters.py
def save_user(self, request, sociallogin, form=None):
    user = super().save_user(request, sociallogin, form)
    user.social_id = sociallogin.account.uid
    user.provider = sociallogin.account.provider
    user.save()
    return redirect('/auth/me//')
