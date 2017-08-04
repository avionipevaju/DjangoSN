import os, json, random, string, sys
from django.shortcuts import render,redirect
from rest_framework.views import APIView
from django.core.files import File
import requests



class Bot(APIView):
    def get(self, request):
        emails = ['alex@alexmaccaw.com','Harlow@clearbit.com','steli@close.io']
        module_dir = os.path.dirname(__file__)
        file_path = os.path.join(module_dir, 'config')
        with open(file_path) as f:
            my_file = File(f)
            j = json.load(my_file)
            number_of_users = int(j['number_of_users'])
            max_post_per_user = int(j['max_posts_per_user'])
            max_likes_per_user = j['max_likes_per_user']

        for index in range(number_of_users):
            session = requests.session()
            username = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5))
            signup_response = session.post('http://localhost:8000/signup/', data = {'username': username,'password': username, 'email':emails[index]})
            r = session.post('http://localhost:8000/login/', data={'username': username, 'password': username})
            for post in range(max_post_per_user):
                content=''.join(random.choice(string.ascii_lowercase + string.digits +string.ascii_uppercase) for _ in range(10))
                post_response=session.post('http://localhost:8000/dashboard/create/', data = {'post':content})
        r = session.get('http://localhost:8000/dashboard/')
        return redirect('index')