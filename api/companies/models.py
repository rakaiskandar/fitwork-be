from django.db import models
import uuid
# Create your models here.

def company_logo_upload_path(instance, filename):
    return f"company_logos/{instance.id}/{filename}"
class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to=company_logo_upload_path, blank=True, null=True)
    career_url = models.CharField(max_length=255)
    mission_statement = models.TextField()
    core_values = models.JSONField(default=list, help_text="List of company values (e.g. Innovation, Integrity)")
    culture_keywords = models.JSONField(default=list, help_text="Descriptive keywords of the company culture")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        evp_changed = True  # Default: anggap berubah

        if self.pk and Company.objects.filter(pk=self.pk).exists():
            old = Company.objects.get(pk=self.pk)
            evp_changed = (
                old.mission_statement != self.mission_statement or
                old.core_values != self.core_values or
                old.culture_keywords != self.culture_keywords
            )

        super().save(*args, **kwargs)

        if evp_changed:
            from api.assessments.ai.generator import generate_questions_from_company
            from api.assessments.models import AssessmentQuestion

            self.questions.all().delete()  # Clear old questions
            questions = generate_questions_from_company(self)

            for q in questions:
                AssessmentQuestion.objects.create(
                    company=self,
                    dimension=q["dimension"],
                    statement=q["statement"],
                    scale=q.get("scale", "Likert")
                )

