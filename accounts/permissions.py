from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """Any logged-in user can read. Only admins can write."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:      # GET, HEAD, OPTIONS
            return True
        return request.user.role == "admin"