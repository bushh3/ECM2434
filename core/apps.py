"""
Author: Zhiqiao Luo, Wayuan Xiao
Configuration class for the 'core' application in the Django project.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
