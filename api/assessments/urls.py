from django.urls import path
from .views import *

urlpatterns = [
    path('assessments/submit/', SubmitAssessmentView.as_view(), name='submit_assessment'),
    path('assessments/question/<uuid:company_id>/', GenerateAssessmentView.as_view(), name='generate_assessment'),
    path('assessments/results/<uuid:company_id>/', AssessmentResultView.as_view(), name='assessment_result'),
    path('assessments/sessions/', UserSessionListView.as_view(), name='user_session_list'),
    path('assessments/compare/', CompareSessionsView.as_view(), name='compare_sessions'),
    path('assessments/overview/<uuid:company_id>/', CompanyAssessmentOverviewView.as_view(), name='company_assessment_overview'),
    path('assessments/company/candidate-sessions/', CompanyCandidateSessionsListView.as_view(), name='company_candidate_sessions_list'),
    path('assessments/session-details/<uuid:session_id>/', SessionDetailView.as_view(), name='session_detail'),
]
