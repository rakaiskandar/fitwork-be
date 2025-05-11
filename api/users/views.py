from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, LoginResponseSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class CustomTokenView(TokenObtainPairView):
    serializer_class = LoginResponseSerializer