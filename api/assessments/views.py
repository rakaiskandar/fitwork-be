from collections import defaultdict
from api.assessments.ai.generator import generate_questions_from_company
from api.assessments.ai.evaluator import evaluate_assessment 
from api.assessments.ai.comparator import evaluate_comparison 
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.common.permissions import IsCompanyAdmin
from api.companies.models import Company
from .models import *
from .serializers import *
from django.db.models import Avg, OuterRef, Subquery, FloatField # Untuk kalkulasi
from django.db.models.functions import Coalesce

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
        
class UserSessionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = AssessmentSession.objects.filter(
            user=request.user
        ).order_by('-created_at')
        serializer = AssessmentSessionSerializer(sessions, many=True)
        return Response(serializer.data)

class SubmitAssessmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AssessmentSubmitSerializer(
            data=request.data, context={'request': request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        session = serializer.save()

        # 1. calculate and save overall
        overall = session.update_overall_score()

        # 2. generate & save AI evaluation
        # collect per-dimension
        answers = session.answers.select_related('question')
        dim_scores = defaultdict(list)
        for ans in answers:
            dim_scores[ans.question.dimension].append(ans.score)
        dimension_results = {
            d: sum(scores) / len(scores) for d, scores in dim_scores.items()
        }
        try:
            summary = evaluate_assessment(
                session.company, overall, dimension_results
            )
            session.set_ai_evaluation(summary)
        except Exception:
            summary = None  # or log

        return Response(
            {
                "message": "Assessment submitted",
                "session": AssessmentSessionSerializer(session).data
            },
            status=201
        )

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

            summary = session.evaluation
            
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
                ],
                "evaluation": summary
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
        result1 = session_scores(sess1)
        result2 = session_scores(sess2)
        
        comp_qs = AssessmentComparison.objects.filter(
            user=user,
            session_a__in=[sess1, sess2],
            session_b__in=[sess1, sess2],
        )
        comp_obj = comp_qs.first()

        # If not found, generate and save a new one
        if not comp_obj:
            try:
                comparison_text = evaluate_comparison(result1, result2)
            except Exception:
                comparison_text = "Comparison analysis unavailable."

            comp_obj = AssessmentComparison.objects.create(
                user=user,
                session_a=sess1,
                session_b=sess2,
                comparison=comparison_text
            )

        # Serialize and return
        serializer = AssessmentComparisonSerializer(comp_obj)
        return Response({
            "session1": result1,
            "session2": result2,
            "comparison": comp_obj.comparison,
            "comparison_record": serializer.data
        })
        
def calculate_overall_score(session):
    avg = AssessmentAnswer.objects.filter(session=session).aggregate(Avg("score"))["score__avg"]
    session.overall_score = avg
    session.save()
    
class CompanyAssessmentOverviewView(APIView):
    """
    Menyediakan overview data assessment untuk sebuah perusahaan,
    termasuk daftar pertanyaan, rata-rata skor tiap pertanyaan dari semua kandidat,
    rata-rata skor keseluruhan perusahaan, dan jumlah total kandidat.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=404)

        # 1. Hitung rata-rata skor keseluruhan untuk perusahaan
        overall_avg_data = AssessmentAnswer.objects.filter(
            session__company_id=company_id
        ).aggregate(overall_company_average_score=Avg('score'))
        
        overall_company_average_score = overall_avg_data.get('overall_company_average_score')
        if overall_company_average_score is not None:
            overall_company_average_score = round(overall_company_average_score, 2)

        # 2. Dapatkan pertanyaan beserta rata-rata skor individualnya dari semua kandidat
        avg_score_per_question_subquery = AssessmentAnswer.objects.filter(
            question_id=OuterRef('pk') # Menggunakan pk untuk merujuk ke primary key AssessmentQuestion
        ).values('question_id').annotate(
            calculated_avg=Avg('score')
        ).values('calculated_avg')

        questions_queryset = AssessmentQuestion.objects.filter(
            company_id=company_id
        ).annotate(
            average_score_all_candidates=Coalesce(
                Subquery(avg_score_per_question_subquery, output_field=FloatField()),
                None # Menggunakan None jika tidak ada skor, akan menjadi null di JSON
            )
        ).order_by('dimension', 'created_at') # Urutkan berdasarkan dimensi lalu tanggal dibuat

        questions_data = []
        for q in questions_queryset:
            avg_score = q.average_score_all_candidates
            questions_data.append({
                "id": str(q.id),
                "statement": q.statement,
                "dimension": q.dimension,
                "average_score_all_candidates": round(avg_score, 2) if avg_score is not None else None
            })
        
        # 3. Hitung jumlah total kandidat (unique users) yang telah mengambil assessment untuk perusahaan ini
        total_candidates = AssessmentSession.objects.filter(
            company_id=company_id
        ).values('user').distinct().count()

        response_data = {
            "company_name": company.name,
            "overall_average_score": overall_company_average_score,
            "total_candidates": total_candidates,
            "questions": questions_data
        }

        return Response(response_data)
    
class CompanyCandidateSessionsListView(APIView): # Contoh jika menggunakan APIView
    permission_classes = [IsAuthenticated, IsCompanyAdmin]

    def get(self, request, *args, **kwargs): # Pastikan metode GET ada dan benar
        user = request.user
        if not user.company_id:
            return Response({"detail": "Admin perusahaan tidak terasosiasi dengan perusahaan."}, status=403)

        queryset = AssessmentSession.objects.filter(company_id=user.company_id)\
                                          .select_related('user', 'company')\
                                          .order_by('-created_at')
        serializer = AdminAssessmentSessionSerializer(queryset, many=True)
        return Response(serializer.data)
    
class SessionDetailView(RetrieveAPIView):
    queryset = AssessmentSession.objects.prefetch_related(
        'answers', 'answers__question', 'user', 'company' # Prefetch for efficiency
    ).all()
    serializer_class = SessionDetailSerializer # Use the detailed serializer
    permission_classes = [IsAuthenticated, IsCompanyAdmin]
    lookup_field = 'id' # Or 'pk' if your URL uses <pk>
    lookup_url_kwarg = 'session_id' # Matches <uuid:session_id> in URL

    def get_object(self):
        # Standard get_object will use queryset, lookup_field, and lookup_url_kwarg
        obj = super().get_object()

        # Verify that the company admin can access this session
        # (i.e., the session belongs to their company)
        user = self.request.user
        if obj.company_id != user.company_id:
            # You can raise a PermissionDenied or return a 404/403 explicitly
            # Raising PermissionDenied is idiomatic for DRF
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to view this assessment session.")
        return obj
