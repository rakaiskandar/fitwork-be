import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from api.companies.models import Company

# Create your models here.
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(unique=True)
    is_candidate = models.BooleanField(default=True)
    is_company_admin = models.BooleanField(default=False)
    is_fitwork_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['username']  

    def __str__(self):
        return self.username
    
