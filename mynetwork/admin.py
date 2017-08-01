from django.contrib import admin
from .models import UserProfile,Post,Likes

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Post)
admin.site.register(Likes)