from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Company
from .serializers import CompanySerializer, UpdateEVPCompanySerializer
from rest_framework.permissions import IsAuthenticated
from api.common.permissions import IsFitworkAdmin, IsOwnerOrFitworkAdmin
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
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
    
class CompanySearchView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        keyword = request.query_params.get('q', '')
        
        queryset = Company.objects.all()
        
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword) |
                Q(mission_statement__icontains=keyword) |
                Q(core_values__icontains=keyword) |
                Q(culture_keywords__icontains=keyword)
            )
        
        serializer = CompanySerializer(queryset.distinct(), many=True)
        return Response(serializer.data)