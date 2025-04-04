"""
Author: Zhiqiao Luo, Wayuan Xiao
Implements a password reset feature based on email, overriding the default method to fetch users by email instead of username.
"""

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model

class EmailBasedPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        """
        Override the get_users() method so that Django looks up the user by email instead of username
        """
        
        active_users = get_user_model()._default_manager.filter(email__iexact=email, is_active=True)
        return (user for user in active_users if user.has_usable_password())