from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomEmailTokenView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='me_profile'),
    path('admin/overview/', AdminPlatformOverviewView.as_view(), name='admin_overview'),
    path('admin/users/', AdminUserListCreateView.as_view(), name='admin_user_list_create'),
    path('admin/users/create/', AdminUserListCreateView.as_view(), name='admin_user_create'),
    path('admin/users/<uuid:pk>/', AdminUserRetrieveUpdateDestroyView.as_view(), name='admin_user_detail_update_delete'),
]
