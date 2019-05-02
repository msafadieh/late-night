'''
    app for gunicorn to use
'''
from flask import Flask, render_template
from .utils import fetch_menu

class LateNight(Flask):
    '''
        extends flask app. also runs a regular page refresher
        on another thread.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_url_rule('/', 'index', self.__index)

    @staticmethod
    def __index():
        """
            The index page with the late night menu items.

            :return HTML page with late menu items.
        """
        return render_template(
            'template.html',
            sorted=sorted,
            stations=fetch_menu())
