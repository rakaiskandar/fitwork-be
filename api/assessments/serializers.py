from collections import defaultdict
from rest_framework import serializers

from api.users.models import User
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

class CandidateUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']

    def get_full_name(self, obj):
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        if obj.first_name:
            return obj.first_name
        if obj.last_name:
            return obj.last_name
        return obj.username

class AdminAssessmentSessionSerializer(serializers.ModelSerializer):
    user = CandidateUserSerializer(read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_id = serializers.UUIDField(source='company.id', read_only=True) # Untuk konfirmasi di frontend jika perlu

    class Meta:
        model = AssessmentSession
        fields = ['id', 'user', 'company_id', 'company_name', 'created_at', 'overall_score']
        
class CandidateUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
    def get_full_name(self, obj):
        if obj.first_name and obj.last_name: return f"{obj.first_name} {obj.last_name}".strip()
        if obj.first_name: return obj.first_name
        if obj.last_name: return obj.last_name
        return obj.username

class AnswerDetailSerializer(serializers.ModelSerializer):
    question_statement = serializers.CharField(source='question.statement', read_only=True)
    dimension = serializers.CharField(source='question.dimension', read_only=True)
    question_id = serializers.UUIDField(source='question.id', read_only=True)
    class Meta:
        model = AssessmentAnswer
        fields = ['question_id', 'question_statement', 'dimension', 'score']

class SessionDetailSerializer(serializers.ModelSerializer):
    user = CandidateUserSerializer(read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    answers = AnswerDetailSerializer(many=True, read_only=True) # Use the AnswerDetailSerializer
    dimension_scores = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentSession
        fields = ['id', 'user', 'company_name', 'created_at', 'overall_score', 'answers', 'dimension_scores']

    def get_dimension_scores(self, obj: AssessmentSession):
        # This method will be called by DRF to populate the 'dimension_scores' field.
        # 'obj' is an instance of AssessmentSession.
        # The view should prefetch 'answers' and 'answers__question' for efficiency.
        
        # Check if answers are already prefetched and available
        # This check might be too simplistic depending on how prefetch_related is used
        # or if it's a fresh instance without prefetched data.
        if not hasattr(obj, 'answers') or not obj.answers.all()._prefetch_done:
             # Fallback or log a warning if answers are not prefetched,
             # as hitting the DB here for each session would be inefficient in a list view.
             # However, for a RetrieveAPIView (single object), it's less critical but still good practice.
             # For this example, we assume answers are available via prefetch or direct query.
             pass


        dim_scores_calc = defaultdict(list)
        # Accessing obj.answers.all() here will trigger a DB query if not prefetched.
        for ans in obj.answers.all(): # Make sure 'answers' is the related_name
            # Ensure ans.question is accessible; select_related('question') on answers is good.
            if hasattr(ans, 'question') and ans.question:
                 dim_scores_calc[ans.question.dimension].append(ans.score)
            else:
                 # Handle case where an answer might not have a question (data integrity issue)
                 # or question was not properly prefetched/selected.
                 pass # Or log this issue

        return {
            dimension: round(sum(scores) / len(scores), 2)
            for dimension, scores in dim_scores_calc.items() if scores
        }

# Your existing AdminAssessmentSessionSerializer can remain for the list view
class AdminAssessmentSessionSerializer(serializers.ModelSerializer):
    user = CandidateUserSerializer(read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_id = serializers.UUIDField(source='company.id', read_only=True)
    class Meta:
        model = AssessmentSession
        fields = ['id', 'user', 'company_id', 'company_name', 'created_at', 'overall_score']