import os
import sys

PROJECT_DIR = "/home/mataheko/credsoft"

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CredSoft.settings")

from CredSoft.wsgi import application