from rest_framework import serializers
from .models import UserProfile, Post


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name', 'location', 'avatar')


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'creator', 'content', 'timestamp', 'like_count')