from rest_framework.permissions import BasePermission


class IsTelescopeUpdatingItself(BasePermission):
    """
    Allow access to telescopes which are updating resources they themselves
    pertain to.
    """

    def has_permission(self, request, view):
        return True  # view.kwargs['pk'] == request.user.telescope.id
