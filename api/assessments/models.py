import uuid
from django.db import models
from api.companies.models import Company
from api.users.models import User
from django.db.models import Avg

# Create your models here.
class AssessmentQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='questions')
    dimension = models.CharField(max_length=100)
    statement = models.TextField()
    scale = models.CharField(max_length=20, default="Likert")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dimension}: {self.statement[:30]}"

class AssessmentSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessments')
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    overall_score = models.FloatField(null=True, blank=True)
    evaluation = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"Session by {self.user.email} on {self.company.name}"
    
    def update_overall_score(self):
        avg = self.answers.aggregate(Avg("score"))["score__avg"]
        self.overall_score = avg
        self.save()
    
    def set_ai_evaluation(self, text: str):
        """Save AI evaluation text."""
        self.evaluation = text
        self.save()

class AssessmentAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(AssessmentSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)
    score = models.IntegerField()
    
    class Meta:
        unique_together = ('session', 'question')

class AssessmentComparison(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comparisons')
    session_a = models.ForeignKey(
        AssessmentSession, on_delete=models.CASCADE, related_name='compared_as_a'
    )
    session_b = models.ForeignKey(
        AssessmentSession, on_delete=models.CASCADE, related_name='compared_as_b'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    comparison = models.TextField()

    class Meta:
        unique_together = ('user', 'session_a', 'session_b')

    def __str__(self):
        return f"Comparison for {self.user.email}: {self.session_a.id} vs {self.session_b.id}"