from django.db import models
import uuid
# Create your models here.

class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    mission_statement = models.TextField()
    core_values = models.JSONField(default=list, help_text="List of company values (e.g. Innovation, Integrity)")
    culture_keywords = models.JSONField(default=list, help_text="Descriptive keywords of the company culture")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nam