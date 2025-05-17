from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, ListAPIView, RetrieveAPIView
from .models import Company
from .serializers import CompanySerializer, UpdateEVPCompanySerializer
from rest_framework.permissions import IsAuthenticated
from api.common.permissions import IsFitworkAdmin, IsOwnerOrFitworkAdmin
from rest_framework.exceptions import PermissionDenied

class CompanyListView(ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

class CompanyDetailView(RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'  # Uses UUID

class CompanyCreateView(CreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsFitworkAdmin]

class CompanyEVPUpdateView(RetrieveUpdateAPIView):
    serializer_class = UpdateEVPCompanySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrFitworkAdmin]
    lookup_field = 'pk'

    def get_object(self):
        user = self.request.user
        pk = self.kwargs.get('pk', None)

        # Route: /companies/my-company/update/
        if not pk:
            if user.is_company_admin and user.company:
                return user.company
            raise PermissionDenied("Only company admins can update their own company.")

        # Route: /companies/<uuid:pk>/update/
        try:
            company = Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            raise PermissionDenied("Company not found.")

        # Check permission via custom IsOwnerOrFitworkAdmin
        self.check_object_permissions(self.request, company)
        return company