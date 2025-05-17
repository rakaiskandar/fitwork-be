from django.urls import path
from .views import CareerConsultationView, ChatHistoryView

urlpatterns = [
    path('ai/consult/', CareerConsultationView.as_view(), name='career_consult'),
    path('ai/history/', ChatHistoryView.as_view(), name='career_history'),
]
