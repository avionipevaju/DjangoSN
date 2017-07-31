from django.db import models
from django.contrib.auth.models import User

class UserProfile(User):
    location=models.CharField(max_length=64)
    avatar=models.CharField(max_length=1024)

class Post(models.Model):
    creator=models.ForeignKey(UserProfile)
    timestamp=models.CharField(max_length=128)
    content=models.CharField(max_length=128)
    likes=models.IntegerField(null=True, blank=True,default=0)

    def get_username(self):
        return self.creator

    def get_avatar(self):
        return self.creator.avatar

    class Meta:
        ordering = ['-timestamp']