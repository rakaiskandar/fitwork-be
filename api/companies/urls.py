from django.urls import path
from .views import *

urlpatterns = [
    path('companies/', CompanyListView.as_view(), name='company_list'),
    path('companies/<uuid:pk>/', CompanyEVPUpdateView.as_view(), name='company_detail_update'),
    path('companies/create/', CompanyCreateView.as_view(), name='company_create'),
]