from django.urls import path
from .views import *

urlpatterns = [
    path('companies/', CompanyListView.as_view(), name='company_list'),
    path('companies/<uuid:pk>/', CompanyDetailView.as_view(), name='company_detail'),
    path('companies/<uuid:pk>/update/', CompanyEVPUpdateView.as_view(), name='company_detail_update'),
    path('companies/my-company/update/', CompanyEVPUpdateView.as_view(), name='company_update_own'),
    path('companies/create/', CompanyCreateView.as_view(), name='company_create'),
]