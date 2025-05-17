from django.urls import path
from .views import GenerateAssessmentView, SubmitAssessmentView

urlpatterns = [
    path('assessments/submit/', SubmitAssessmentView.as_view(), name='submit_assessment'),
    path('assessments/question/<uuid:company_id>/', GenerateAssessmentView.as_view(), name='generate_assessment'),
]
