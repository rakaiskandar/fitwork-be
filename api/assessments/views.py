from api.assessments.ai.gemini_langchain import generate_questions_from_company
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.companies.models import Company
from .models import AssessmentQuestion
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