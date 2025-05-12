from rest_framework.permissions import BasePermission

class IsFitworkAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_fitwork_admin

class IsCompanyAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_company_admin