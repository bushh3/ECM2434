from django.contrib.auth.backends import ModelBackend
from core.models import CustomUser

class EmailAuthBackend(ModelBackend):
    """
    自定义认证后端，允许使用 email 登录
    """
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(email=email)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None
        return None