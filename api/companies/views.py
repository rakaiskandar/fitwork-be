from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, ListAPIView
from .models import Company
from .serializers import CompanySerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from api.common.permissions import IsFitworkAdmin, IsOwnerOrFitworkAdmin

class CompanyListView(ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class CompanyCreateView(CreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsFitworkAdmin]

class CompanyEVPUpdateView(RetrieveUpdateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrFitworkAdmin]
    lookup_field = 'pk'