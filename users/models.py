# users/models.py
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_no = models.CharField(max_length=15, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True)

    def __str__(self):
        return self.user.username
