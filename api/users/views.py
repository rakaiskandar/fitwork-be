from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
from api.common.permissions import *

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class CustomEmailTokenView(TokenObtainPairView):
    serializer_class = CustomEmailTokenSerializer

class RegisterCompanyAdminView(generics.CreateAPIView):
    serializer_class = RegisterCompanyAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsFitworkAdmin]