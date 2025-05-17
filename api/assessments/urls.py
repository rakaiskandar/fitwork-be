from django.urls import path
from .views import AssessmentResultView, GenerateAssessmentView, SubmitAssessmentView

urlpatterns = [
    path('assessments/submit/', SubmitAssessmentView.as_view(), name='submit_assessment'),
    path('assessments/question/<uuid:company_id>/', GenerateAssessmentView.as_view(), name='generate_assessment'),
    path('assessments/results/<uuid:company_id>/', AssessmentResultView.as_view(), name='assessment_result'),
]
