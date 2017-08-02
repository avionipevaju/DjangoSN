import os
import json
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.files import File

# Create your views here.
class Bot(APIView):
    def get(self, request):
        module_dir = os.path.dirname(__file__)
        file_path = os.path.join(module_dir, 'config')
        with open(file_path) as f:
            myFile=File(f)
            j=json.load(myFile)
            return Response(j)