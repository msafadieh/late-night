'''
    app for gunicorn to use
'''
from datetime import datetime
from flask import Flask, render_template
from .utils import fetch_menu

class LateNight(Flask):
    '''
        extends flask app. also runs a regular page refresher
        on another thread.
    '''
    def __init__(self):
        Flask.__init__(self, 'Late Night')

        self.add_url_rule(
            '/',
            view_func=lambda: render_template(
                'template.html',
                date_time=datetime.now().strftime("%a %x %I:%M %p"),
                sorted=sorted,
                stations=fetch_menu())
            )
