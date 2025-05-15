from rest_framework import serializers
from .models import AssessmentQuestion, AssessmentSession, AssessmentAnswer

class AssessmentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentQuestion
        fields = '__all__'

class AssessmentSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentSession
        fields = '__all__'

class AssessmentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentAnswer
        fields = '__all__'
