from collections import defaultdict
from api.assessments.ai.generator import generate_questions_from_company
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.companies.models import Company
from .models import AssessmentQuestion, AssessmentSession, AssessmentAnswer
from .serializers import AssessmentQuestionSerializer, AssessmentSubmitSerializer, AssessmentSessionSerializer
from django.db.models import Avg

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
                    "questions": AssessmentQuestionSerializer(existing, many=True).data,
                    "name": company.name
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
            calculate_overall_score(session)  # ✅ Panggil di sini setelah jawaban disimpan
            return Response({"message": "Assessment submitted", "session_id": str(session.id)}, status=201)
        return Response(serializer.errors, status=400)


class UserSessionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = AssessmentSession.objects.filter(
            user=request.user
        ).order_by('-created_at')
        serializer = AssessmentSessionSerializer(sessions, many=True)
        return Response(serializer.data)

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
        
class CompareSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        s1 = request.query_params.get('s1')
        s2 = request.query_params.get('s2')
        user = request.user

        if not s1 or not s2:
            return Response({"error": "Provide s1 and s2 session IDs."}, status=400)

        try:
            sess1 = AssessmentSession.objects.get(id=s1, user=user)
            sess2 = AssessmentSession.objects.get(id=s2, user=user)
        except AssessmentSession.DoesNotExist:
            return Response({"error": "Session not found or not yours."}, status=404)

        def session_scores(sess):
            dim_scores = defaultdict(list)
            for ans in sess.answers.select_related('question'):
                dim_scores[ans.question.dimension].append(ans.score)

            per_dim = {d: round(sum(scores)/len(scores), 2) for d, scores in dim_scores.items()}
            overall = round(sum([s for sc in dim_scores.values() for s in sc]) / sess.answers.count(), 2)
            return {
                "session_id": str(sess.id),
                "company": sess.company.name,
                "created_at": sess.created_at,
                "overall_score": overall,
                "dimension_scores": per_dim
            }

        return Response({
            "session1": session_scores(sess1),
            "session2": session_scores(sess2),
        })
        
def calculate_overall_score(session):
    avg = AssessmentAnswer.objects.filter(session=session).aggregate(Avg("score"))["score__avg"]
    session.overall_score = avg
    session.save()
    

