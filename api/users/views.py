from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
from api.common.permissions import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

class CustomEmailTokenView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomEmailTokenSerializer

class RegisterCompanyAdminView(generics.CreateAPIView):
    serializer_class = RegisterCompanyAdminSerializer
    permission_classes = [IsAuthenticated, IsFitworkAdmin]

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)