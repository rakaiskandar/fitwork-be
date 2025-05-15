import uuid
from django.db import models
from api.companies.models import Company
from api.users.models import User

# Create your models here.
class AssessmentQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='questions')
    dimension = models.CharField(max_length=100)
    statement = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dimension}: {self.statement[:30]}"

class AssessmentSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessments')
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    overall_score = models.FloatField(null=True, blank=True)

class AssessmentAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(AssessmentSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)
    score = models.IntegerField()