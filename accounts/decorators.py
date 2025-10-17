from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(allowed_roles=[]):
    """
    Custom decorator to restrict access based on user role.
    Example usage:
    @role_required(["admin", "superadmin"])
    def dashboard(request): ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                # redirect to login if not logged in
                return redirect('accounts:login')

            # check if user has a related Member object with role
            if hasattr(request.user, 'member'):
                user_role = request.user.member.role
                if user_role in allowed_roles:
                    return view_func(request, *args, **kwargs)

            # if not allowed, raise 403 error
            raise PermissionDenied

        return wrapper
    return decorator
