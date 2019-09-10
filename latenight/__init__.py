'''
    app for gunicorn to use
'''
from flask import Flask, render_template
from .utils import fetch_menu

app = Flask(__name__)


@app.route("/")
def index():
"""
    The index page with the late night menu items.

    :return HTML page with late menu items.
"""
    return render_template(
        'template.html',
        sorted=sorted,
        stations=fetch_menu())
