from rest_framework import serializers
from .models import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'career_url', 'logo',
            'mission_statement', 'core_values', 'culture_keywords'
        ]
        read_only_fields = ['id']

class UpdateEVPCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['name', 'logo', 'career_url', 'mission_statement', 'core_values', 'culture_keywords']
