from datetime import datetime
import json
import requests
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.response import Response
from django.shortcuts import render,redirect
from django.db import IntegrityError
from django.http import HttpResponse
from pyhunter import PyHunter
import clearbit
from .models import UserProfile,Post,Like
from .serializers import UserSerializer,PostSerializer


class Home(APIView):
    def get(self, request):
        if request.session.get('user') is not None:
            return redirect('dashboard')
        error = request.session.get('error')
        if error is not None:
            return render(request, 'index.html', {'error': error})
        else:
            return render(request, 'index.html')


class Signup(APIView):
    def get(self, request):
        return render(request, 'signup.html')

    def post(self, request):
        apikey = '49f3182ed78514853b35649a89d11bd29e2650fe'
        clearbit.key = 'sk_1d89e1a6b67c5e4e6934cf11d0460bea'

        hunter = PyHunter(apikey)
        email = request.POST['email']

        if request.POST['email'] == '' or request.POST['username'] == '' or request.POST['password'] == '':
            return render(request, 'signup.html', {'error': 'Form not filled correctly'})

        result = hunter.email_verifier(email)

        if result['result'] != 'undeliverable':

            lookup = clearbit.Enrichment.find(email=email, stream=True)

            if 'person' in lookup:
                mail = lookup['person']['email']
                first_name = lookup['person']['name']['givenName']
                last_name = lookup['person']['name']['familyName']
                location = lookup['person']['location']
                avatar = lookup['person']['avatar']

                new_user = UserProfile(
                    username=request.POST['username'], email=mail,
                    first_name=first_name, last_name=last_name,
                    avatar=avatar, location=location)
                new_user.set_password(request.POST['password'])

                try:
                    serializer = UserSerializer(new_user)
                    request.session['user'] = serializer.data
                    new_user.save()
                except IntegrityError:
                    return render(request, 'signup.html',
                                  {'error': 'User with the same username or email already exists'})
                return redirect('index')
            else:
                return HttpResponse('NOT FOUND')
        else:
            return render(request, 'signup.html', {'error': 'The given email doesnt exist'})


class Profile(APIView):
    def get(self, request):
        current_user = request.session.get('user')
        return render(
            request, 'profile.html',
            {'email': current_user['email'], 'full_name': current_user['first_name']+' '+current_user['last_name'],
             'location': current_user['location'], 'avatar': current_user['avatar'],
             'username': current_user['username']})


class Login(APIView):
    def post(self, request):
        try:
            user = UserProfile.objects.get(username=request.POST['username'])
        except UserProfile.DoesNotExist:
            request.session['error'] = 'Not registered. Please Sign up'
            return redirect('index')

        success = user.check_password(request.POST['password'])

        if success:
            serializer = UserSerializer(user)
            request.session['user'] = serializer.data
            request.session['error'] = ' '
            session = requests.session()
            r = session.post('http://localhost:8000/api-token-auth/', data={'username': user.username,
                                                                            'password': request.POST['password']})
            token = (json.loads(r.text))['token']
            headers = dict(Authorization='Bearer'+token)
            r = requests.get('http://localhost:8000/dashboard/', headers=headers)
            #return HttpResponse(r)
            return redirect('dashboard')
        else:
            request.session['error'] = 'Wrong credentials'
            return redirect('index')


class Dashboard(APIView):
    #authentication_classes = (JSONWebTokenAuthentication,)
    def get(self, request):
        if request.GET.get('logout', False) is not False:
            request.session['user'] = None
            return redirect('index')

        current_user = request.session.get('user')
        post_list = Post.objects.all()
        return render(request, 'dashboard.html', {'post_list': post_list, 'username': current_user['username'],
                                                  'avatar': current_user['avatar']})

    def post(self, request):
        post = Post.objects.get(id=request.POST['id'])
        current_user = request.session.get('user')
        user = UserProfile.objects.get(id=current_user['id'])
        if post.creator == user:
            return redirect('dashboard')
        try:
            like = Like.objects.get(post=post, liked_by=user)
            post.like_count = post.like_count - 1
            like.delete()
        except Like.DoesNotExist:
            like = Like(post=post, liked_by=user)
            post.like_count = post.like_count + 1
            like.save()
        post.save()
        return redirect('dashboard')


class CreatePost(APIView):
    def post(self, request):
        current_user = request.session.get('user')
        content = request.POST['post']
        user = UserProfile.objects.get(id=current_user['id'])
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        new_post = Post(content=content, timestamp=timestamp, creator=user)
        new_post.save()
        return redirect('dashboard')