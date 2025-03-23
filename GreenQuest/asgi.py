"""
Author: Wayuan Xiao, Zhiqiao Luo

ASGI config for GreenQuest project.

"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GreenQuest.settings')

application = get_asgi_application()
