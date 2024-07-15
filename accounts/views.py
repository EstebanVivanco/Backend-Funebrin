from django.shortcuts import render
from rest_framework import viewsets
from .serializers import UserSerializer
from .models import User
from utils.swagger_utils import CustomTags

# Create your views here.'

@CustomTags.accounts
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

