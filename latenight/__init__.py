'''
    app for gunicorn to use
'''
from .client import LateNight

MAIN = LateNight()
