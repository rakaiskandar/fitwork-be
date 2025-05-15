from django.urls import path
from .views import GenerateAssessmentView

urlpatterns = [
    path('ai/generate/<uuid:company_id>/', GenerateAssessmentView.as_view(), name='generate-assessment'),
]
