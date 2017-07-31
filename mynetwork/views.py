from django.shortcuts import render,redirect
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from django.db import IntegrityError
from .models import UserProfile,Post
from .serializers import UserSerializer,PostSerializer
from django.http import HttpResponse
import requests
from pyhunter import PyHunter
import clearbit
import jwt
from datetime import datetime, timedelta

class Home(APIView):
   def get(self,request):
       error=request.session.get('error')
       if error != None:
           return render(request,'index.html',{'error':error})
       else:
           return render(request,'index.html')

class Signup(APIView):

    def get(self,request):
        return render(request,'signup.html')

    def post(self, request):
        apikey = '49f3182ed78514853b35649a89d11bd29e2650fe'
        clearbit.key = 'sk_1d89e1a6b67c5e4e6934cf11d0460bea'

        hunter=PyHunter(apikey)
        email=request.POST['email']

        if request.POST['email']=='' or request.POST['username']=='' or request.POST['password']=='':
            return render(request, 'signup.html',{'error':'Form not filled correctly'})

        result = hunter.email_verifier(email)

        if result['result']!='undeliverable':

            lookup = clearbit.Enrichment.find(email=email, stream=True)

            if 'person' in lookup:
                mail=lookup['person']['email']
                first_name=lookup['person']['name']['givenName']
                last_name = lookup['person']['name']['familyName']
                location=lookup['person']['location']
                avatar=lookup['person']['avatar']

                new_user=UserProfile(username=request.POST['username'],email=mail,first_name=first_name,last_name=last_name,avatar=avatar,location=location)
                new_user.set_password(request.POST['password'])

                try:
                    serializer=UserSerializer(new_user)
                    request.session['user'] = serializer.data
                    new_user.save()
                except IntegrityError:
                    return render(request, 'signup.html', {'error': 'User with the same username or email alerady exists'})
                return redirect('profile')
            else:
                return HttpResponse('NOT FOUND')
        else:
            return render(request, 'signup.html', {'error': 'The given email doesnt exist'})

class Profile(APIView):
    def get(self,request):
        currentUser=request.session.get('user')
        return render(request, 'profile.html',
                      {'email': currentUser['email'], 'full_name': currentUser['first_name']+' '+currentUser['last_name'], 'location': currentUser['location'], 'avatar': currentUser['avatar'],
                       'username': currentUser['username']})

class Login(APIView):

    def post(self,request):

        try:
           user = UserProfile.objects.get(username=request.POST['username'])
        except UserProfile.DoesNotExist:
            request.session['error'] = 'Not registered. Please Sign up'
            return redirect('index')


        success=user.check_password(request.POST['password'])

        if success:
            serializer = UserSerializer(user)
            request.session['user'] = serializer.data
            request.session['error'] = ' '
            return redirect('dashboard')
        else:
            request.session['error'] = 'Wrong credentials'
            return redirect('index')

class Dashboard(APIView):
    def get(self,request):
        currentUser=request.session.get('user')
        post_list = Post.objects.all()
        return render(request, 'dashboard.html', {'post_list': post_list, 'username': currentUser['username'],'avatar':currentUser['avatar']})

    def post(self,request):
        post=Post.objects.get(id=request.POST['id'])
        post.likes=post.likes+1
        post.save()
        return redirect('dashboard')

class CreatePost(APIView):
    def post(self,request):
        currentUser=request.session.get('user')
        content=request.POST['post']
        user=UserProfile.objects.get(id=currentUser['id'])
        timestamp=datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        new_post=Post(content=content,timestamp=timestamp,creator=user)
        new_post.save()
        return redirect('dashboard')

class LikePost(APIView):
    def post(self,request):
        post=Post.objects.get(id=request.POST['id'])
        post.likes=post.likes+1
        post.save()
        serializer=PostSerializer(post)
        return redirect('dashboard')

class UserList(APIView):
    def get(self,request,format=None):
        users = UserProfile.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self,request,format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetail(APIView):
    def get_Object(self,pk):
        try:
            return UserProfile.objects.get(pk=pk)
        except UserProfile.DoesNotExist:
            raise Http404

    def get(self,request,pk,format=None):
        serializer = UserSerializer(self.get_Object(pk))
        return Response(serializer.data)

    def put(self,request,pk,format=None):
        serializer = UserSerializer(self.get_Object(pk), data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        self.get_Object(pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)