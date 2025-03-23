"""
Author: Zhiqiao Luo, Wayuan Xiao
Custom backend allowing email-based user authentication.
"""


from django.contrib.auth.backends import ModelBackend
from core.models import CustomUser

class EmailAuthBackend(ModelBackend):
    """
    Customize the authentication backend, allowing email login
    """
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(email=email)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None
        return None