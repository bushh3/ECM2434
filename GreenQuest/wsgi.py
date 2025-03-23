"""
Author: Wayuan Xiao, Zhiqiao Luo
WSGI config for GreenQuest project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GreenQuest.settings')

application = get_wsgi_application()
