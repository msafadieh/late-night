'''
    Fetches a list of food items being served
    at late night.
'''
from datetime import datetime
import json
from threading import Thread
from os import listdir, remove
from os.path import isfile
from re import findall, fullmatch
from time import sleep
from flask import Flask
from requests import get

# regular expressions used to fetch dictionaries and station names
MENU_ITEMS_REGEX = r"Bamco\.menu_items = ({(?:.+:.+,?)+})"
LATE_NIGHT_REGEX = r"Bamco\.dayparts\[\'7\'\] = ({(?:.+:.+,?)+})"
STATION_REGEX = r"<strong>@?(.+)<\/strong>"
FILE_NAME_PATTERN = r"[0-9]{6}.html"
LABELS_DICT = {"9": "Gluten-Free"}

def fetch_menu():
    '''
        makes a GET request to CBA's website and parses HTML
        file to find menu items.
    '''
    req = get('https://vassar.cafebonappetit.com/').text
    time = datetime.now().strftime("%a %x %I:%M %p")

    menu_data = findall(MENU_ITEMS_REGEX, req)
    
    if menu_data:
        menu_items = json.loads(menu_data[0])
        
        late_night_data = findall(LATE_NIGHT_REGEX, req)
    
        if late_night_data:
            late_night_menu = json.loads(late_night_data[0])

            stations = late_night_menu['stations']
            for station in stations:
                if station['label'] == 'Gordon Commons':
                    items = station['items']
            return [menu_items.get(item) for item in items], time

    return [], None

def parse_as_html(menu, time):
    '''
        parses elements as an html webpage
    '''
    if not menu:
        string = "<h1>No food on the menu tonight.</h1>"

    else:
        template = open("template.html", "r").read()
        stations = dict()

        for item in menu:
            item_name = item.get('label').capitalize()
            cor_icon = item.get('cor_icon')

            # cor_icon is [] and not {} when empty
            if cor_icon:
                labels_list = sorted(LABELS_DICT.get(key, value) for key, value in cor_icon.items())
                labels = ', '.join(labels_list)
            else:
                labels = ""

            item_string = f"{item_name} ({labels})" if labels else item_name
            station = findall(STATION_REGEX, item.get('station'))[0].title()
            stations.setdefault(station, [])
            stations[station].append(item_string)

        string = ""

        for station in sorted(stations.keys()):
            string += f"\n    <h2>{station}:</h2>"

            items = sorted(stations[station])
            nline = '\n      '
            string += f'''
        <ul>
        {nline.join(f'<li>{item}</li>' for item in items)}
        </ul>'''

        string += f"\n    <p>Last updated: {time}</p>"

    return template.replace("[MENU_PLACEHOLDER]", string)

def generate_name():
    '''
        generates file name from current date
    '''
    return f"{datetime.now().strftime('%d%m%y')}.html"

def generate_file_every_15_min():
    '''
        updates the saved menu file every
        15 minutes
    '''
    while True:
        name = generate_name()
        if not isfile(name):
            generate_html_file(name)
            clean_old_pages(name)
        else:
            generate_html_file(name)
        sleep(900)

def generate_html_file(path):
    '''
        generates HTML file and writes it to file
    '''
    menu, time = fetch_menu()
    html = parse_as_html(menu, time)

    with open(path, 'w') as file:
        file.write(html)

    return html

def clean_old_pages(name):
    '''
        removes old HTML pages
    '''
    files = listdir()
    deleted = []
    for file in files:
        if fullmatch(FILE_NAME_PATTERN, file) and file != name:
            deleted.append(file)
            remove(file)
    return deleted

def index():
    '''
        creates an HTML file called "DDMMYY.html" with the list of late night
        items if no file was found.
    '''
    name = generate_name()

    if isfile(name):
        html = open(name).read()
    else:
        html = generate_html_file(name)
        clean_old_pages(name)

    return html

class LateNight(Flask):
    '''
        extends flask app. also runs a regular page refresher
        on another thread.
    '''
    def __init__(self):
        self.__refresh = Thread(target=generate_file_every_15_min, daemon=True)
        self.__refresh.start()

        Flask.__init__(self, 'Late Night')
        self.add_url_rule('/', view_func=index)
        self.add_url_rule('/.well-known/acme-challenge/MCkyH-5D3dRO3odstSj2UQUxRaTfKGtemCe1SsjQ0N4', view_func=challenge)

def challenge():
    return "MCkyH-5D3dRO3odstSj2UQUxRaTfKGtemCe1SsjQ0N4.QyXe7It5hbuHumhBAlNLybhSZjYLALqLSM3gPLe2QEc"