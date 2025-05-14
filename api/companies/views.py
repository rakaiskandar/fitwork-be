from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, ListAPIView, RetrieveAPIView
from .models import Company
from .serializers import CompanySerializer, UpdateEVPCompanySerializer
from rest_framework.permissions import IsAuthenticated
from api.common.permissions import IsFitworkAdmin, IsOwnerOrFitworkAdmin

class CompanyListView(ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsFitworkAdmin]

class CompanyDetailView(RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrFitworkAdmin]
    lookup_field = 'pk'  # Uses UUID

class CompanyCreateView(CreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsFitworkAdmin]

class CompanyEVPUpdateView(RetrieveUpdateAPIView):
    serializer_class = UpdateEVPCompanySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrFitworkAdmin]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        if user.is_fitwork_admin:
            return Company.objects.all()
        if user.is_company_admin and user.company:
            return Company.objects.filter(pk=user.company.pk)
        return Company.objects.none()
