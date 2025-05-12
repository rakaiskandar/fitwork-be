from django.urls import path
from .views import *

urlpatterns = [
    path('companies/', CompanyViewSet.as_view(), name='company_read'),
]