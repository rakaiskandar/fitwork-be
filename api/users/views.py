from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
from api.common.permissions import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from api.users.models import User
from api.companies.models import Company
from api.assessments.models import AssessmentQuestion, AssessmentSession
from django.db.models import Avg, Count
from rest_framework.generics import CreateAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView

class RegisterView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

class CustomEmailTokenView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomEmailTokenSerializer

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
            "is_candidate": user.is_candidate,
            "is_company_admin": user.is_company_admin,
            "is_fitwork_admin": user.is_fitwork_admin,
            "company_id": user.company_id
        })

class AdminPlatformOverviewView(APIView):
    permission_classes = [IsAuthenticated, IsFitworkAdmin]

    def get(self, request, *args, **kwargs):
        try:
            total_companies = Company.objects.count()

            total_candidates_registered = User.objects.filter(is_candidate=True).count()

            total_assessments_completed = AssessmentSession.objects.filter(overall_score__isnull=False).count()

            MAX_DIMENSIONS_TO_SHOW = 10  # You can adjust this number

            annotated_dimensions_with_counts = AssessmentQuestion.objects.values('dimension').annotate(
                avg_score_raw=Avg('assessmentanswer__score'),
                num_answers=Count('assessmentanswer__id')  # Count answers linked to questions of this dimension
            ).filter(num_answers__gt=0).order_by('-num_answers', 'dimension') # Ensure num_answers > 0

            top_n_dimensions_data = []
            for item in annotated_dimensions_with_counts[:MAX_DIMENSIONS_TO_SHOW]: # Slice to get top N
                top_n_dimensions_data.append({
                    "dimension": item['dimension'],
                    "average_score": round(item['avg_score_raw'], 2) if item['avg_score_raw'] is not None else None,
                })
            
            data = {
                "total_companies": total_companies,
                "total_candidates_registered": total_candidates_registered,
                "total_assessments_completed": total_assessments_completed,
                "average_scores_by_dimension": top_n_dimensions_data, # Use the curated list
            }
            return Response(data)

        except Exception as e:
            return Response(
                {"error": "An error occurred while fetching platform overview data.", "detail": str(e)},
                status=500 # Internal Server Error
            )

class AdminUserListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsFitworkAdmin]
    
    def get_queryset(self):
        return User.objects.filter(is_fitwork_admin=False).select_related('company').order_by('email')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdminUserCreateSerializer
        return AdminUserListSerializer

    def perform_create(self, serializer):
        serializer.save(is_fitwork_admin=False)

class AdminUserRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = AdminUserUpdateSerializer 
    permission_classes = [IsAuthenticated, IsFitworkAdmin]
    lookup_field = 'pk'

    def get_queryset(self):
        return User.objects.filter(is_fitwork_admin=False)

    def get_serializer_class(self):
        if self.request.method == 'GET': 
            return AdminUserListSerializer 
        return AdminUserUpdateSerializer

    def perform_update(self, serializer):
        serializer.save(is_fitwork_admin=False)

    def perform_destroy(self, instance):
        if instance == self.request.user: # Should not happen if queryset excludes self
            raise serializers.ValidationError({"detail": "You cannot delete your own account through this admin interface."}) 
        super().perform_destroy(instance)