from rest_framework import serializers
from .models import AssessmentQuestion, AssessmentSession, AssessmentAnswer, AssessmentComparison

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

class AnswerInputSerializer(serializers.Serializer):
    question_id = serializers.UUIDField()
    score = serializers.IntegerField(min_value=1, max_value=5)

class AssessmentSubmitSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    answers = AnswerInputSerializer(many=True)

    def create(self, validated_data):
        user = self.context['request'].user
        company_id = validated_data['company_id']
        answers_data = validated_data['answers']

        session = AssessmentSession.objects.create(
            user=user,
            company_id=company_id
        )

        for ans in answers_data:
            AssessmentAnswer.objects.create(
                session=session,
                question_id=ans['question_id'],
                score=ans['score']
            )

        return session

class AssessmentSessionSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = AssessmentSession
        fields = ['id', 'company', 'company_name', 'created_at', 'overall_score', 'evaluation']
        read_only_fields = fields

class AssessmentComparisonSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentComparison
        fields = ['id', 'session_a', 'session_b', 'comparison', 'created_at']
        read_only_fields = fields
