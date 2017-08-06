import os, json, random, string, sys
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.files import File
from django.http import HttpResponse
from django.db.models import Q
import requests
from mynetwork.models import UserProfile,Post
from mynetwork.serializers import UserSerializer, PostSerializer

emails = ['alex@alexmaccaw.com', 'Harlow@clearbit.com', 'steli@close.io']
module_dir = os.path.dirname(__file__)
file_path = os.path.join(module_dir, 'config')
with open(file_path) as f:
    my_file = File(f)
    j = json.load(my_file)
    number_of_users = int(j['number_of_users'])
    max_post_per_user = int(j['max_posts_per_user'])
    max_likes_per_user = int(j['max_likes_per_user'])


def signup_user(session, index):
    username = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5))
    session.post('http://localhost:8000/signup/', data={'username': username,
                                                        'password': username, 'email': emails[index]})
    session.post('http://localhost:8000/login/', data={'username': username, 'password': username})


def create_post(session):
    content = ''.join(random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in range(10))
    session.post('http://localhost:8000/dashboard/create/', data={'post': content})


def get_user_list():
    all_users = UserProfile.objects.all()
    serializer = UserSerializer(all_users, many=True)
    users = {}
    for data in serializer.data:
        post_count = Post.objects.filter(creator=data['id']).count()
        users[data['id']] = post_count

    sorted_users = sorted(users.items(), key=lambda x: x[1], reverse=True)
    return sorted_users


def get_next_user(users, count):
    for u in users:
        sc = Post.objects.filter(~Q(creator=int(u[0])), like_count=0)
        if sc.count() != 0 and count[u[0]] != 0:
            return u
    return None


def get_count(users):
    count = {}
    for user in users:
        count[user[0]] = max_likes_per_user
    return count


class Bot(APIView):
    def get(self, request):
        session = requests.session()
        for index in range(number_of_users):
            signup_user(session, index)
            for post in range(random.randrange(max_post_per_user)+1):
                create_post(session)

        users = get_user_list()
        count = get_count(users)

        while True:
            user = get_next_user(users, count)
            if user is None:
                break
            u = UserProfile.objects.get(id=user[0])
            serializer = UserSerializer(u)
            session.post('http://localhost:8000/login/', data={'username': serializer.data['username'],
                                                               'password': serializer.data['username']})
            posts = Post.objects.filter(~Q(creator=u))
            serializer = PostSerializer(posts, many=True)
            post = random.choice(serializer.data)
            post_id = post['id']
            post_count = Post.objects.filter(creator=int(post['creator']), like_count=0).count()
            if post_count > 0:
                session.post('http://localhost:8000/dashboard/', data={'id': post_id})
                count[user[0]] = count[user[0]] - 1
            s = Post.objects.filter(like_count=0)
            if s.count() == 0:
                break
        return redirect('index')
