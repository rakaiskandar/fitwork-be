from django.urls import path
from .views import CareerConsultationView, ChatSessionDetailView,ChatSessionListView

urlpatterns = [
    path('ai/consult/', CareerConsultationView.as_view(), name='career_consult'),
    path("ai/history/<uuid:session_id>/", ChatSessionDetailView.as_view(), name="career_history_detail"),
    path("ai/sessions/", ChatSessionListView.as_view(), name="career_session_list"),
]
