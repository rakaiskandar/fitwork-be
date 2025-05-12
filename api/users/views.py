from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, CustomEmailTokenSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class CustomEmailTokenView(TokenObtainPairView):
    serializer_class = CustomEmailTokenSerializer