from django.urls import path
from .views import *

urlpatterns = [
    path('assessments/submit/', SubmitAssessmentView.as_view(), name='submit_assessment'),
    path('assessments/question/<uuid:company_id>/', GenerateAssessmentView.as_view(), name='generate_assessment'),
    path('assessments/results/<uuid:company_id>/', AssessmentResultView.as_view(), name='assessment_result'),
    path('assessments/sessions/', UserSessionListView.as_view(), name='user_session_list'),
    path('assessments/compare/', CompareSessionsView.as_view(), name='compare_sessions'),
]
