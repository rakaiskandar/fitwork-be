from rest_framework.permissions import BasePermission

class IsFitworkAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_fitwork_admin

class IsCompanyAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and 
                    request.user.is_authenticated and 
                    request.user.is_company_admin and
                    request.user.company_id) 
        
class IsOwnerOrFitworkAdmin(BasePermission):
    """
    Only company admins can update their own company.
    Fitwork admins can update any company.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            user.is_authenticated and (
                user.is_fitwork_admin or
                (user.is_company_admin and user.company == obj)
            )
        )