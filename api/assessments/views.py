from collections import defaultdict
from api.assessments.ai.generator import generate_questions_from_company
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.companies.models import Company
from .models import AssessmentQuestion, AssessmentSession
from .serializers import AssessmentQuestionSerializer, AssessmentSubmitSerializer

class GenerateAssessmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, company_id):
        force = request.query_params.get("force", "false").lower() == "true"

        try:
            company = Company.objects.get(id=company_id)

            existing = company.questions.all()
            if existing.exists() and not force:
                return Response({
                    "message": "Assessment already exists for this company.",
                    "questions": AssessmentQuestionSerializer(existing, many=True).data
                }, status=200)

            # Delete old if regenerating
            if existing.exists():
                existing.delete()

            # Generate new questions
            questions = generate_questions_from_company(company)
            created = []

            for q in questions:
                question = AssessmentQuestion.objects.create(
                    company=company,
                    dimension=q["dimension"],
                    statement=q["statement"],
                    scale=q.get("scale", "Likert")
                )
                created.append(question)

            return Response({
                "message": "Assessment generated.",
                "questions": AssessmentQuestionSerializer(created, many=True).data
            }, status=201)

        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class SubmitAssessmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AssessmentSubmitSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            session = serializer.save()
            return Response({"message": "Assessment submitted", "session_id": str(session.id)}, status=201)
        return Response(serializer.errors, status=400)

class AssessmentResultView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
            session = AssessmentSession.objects.filter(user=request.user, company=company).order_by('-created_at').first()

            if not session:
                return Response({"error": "You haven't taken an assessment for this company."}, status=404)

            answers = session.answers.select_related('question')
            dimension_scores = defaultdict(list)

            # Group scores by dimension
            for ans in answers:
                dimension_scores[ans.question.dimension].append(ans.score)

            # Calculate per-dimension average
            dimension_results = {
                dimension: round(sum(scores) / len(scores), 2)
                for dimension, scores in dimension_scores.items()
            }

            overall = round(sum([s for sl in dimension_scores.values() for s in sl]) / answers.count(), 2)

            return Response({
                "company": company.name,
                "user": request.user.email,
                "overall_score": overall,
                "dimensions": dimension_results,
                "answers": [
                    {
                        "question": ans.question.statement,
                        "dimension": ans.question.dimension,
                        "score": ans.score
                    }
                    for ans in answers
                ]
            })

        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=404)