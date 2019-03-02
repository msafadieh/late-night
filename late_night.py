# pylint: disable = pointless-string-statement, broad-except
'''
    Fetches a list of food items being served
    at late night.
'''
from datetime import datetime
import json
from multiprocessing import Process
from os.path import isfile
from re import findall
from time import sleep
from flask import Flask
from requests import get

# regular expressions used to fetch dictionaries and station names
MENU_ITEMS_REGEX = r"Bamco\.menu_items = ({(?:.+:.+,?)+})"
LATE_NIGHT_REGEX = r"Bamco\.dayparts\[\'7\'\] = ({(?:.+:.+,?)+})"
STATION_REGEX = r"<strong>@?(.+)<\/strong>"
LABELS_DICT = {}

FLASK_APP = Flask('Late Night')

def fetch_menu():
    '''
        makes a GET request to CBA's website and parses HTML
        file to find menu items.
    '''
    req = get('https://vassar.cafebonappetit.com/').text
    time = datetime.now().strftime("%a %x %I:%M %p")

    menu_data = findall(MENU_ITEMS_REGEX, req)[0]
    menu_items = json.loads(menu_data)

    late_night_data = findall(LATE_NIGHT_REGEX, req)[0]
    late_night_menu = json.loads(late_night_data)

    stations = late_night_menu['stations']
    for station in stations:
        if station['label'] == 'Gordon Commons':
            items = station['items']
            return [menu_items.get(item) for item in items], time

    return [], None

def parse_results(menu):
    '''
        uses the menu items found using the fetch_menu() function
        to generate a well-formatted string (organized by location).
    '''
    stations = dict()

    for item in menu:
        item_name = item.get('label').capitalize()
        cor_icon = item.get('cor_icon')

        # cor_icon is [] and not {} when empty
        labels = ', '.join(sorted(cor_icon.values())) if cor_icon else ""

        item_string = f"{item_name} ({labels})" if labels else item_name
        station = findall(STATION_REGEX, item.get('station'))[0].title()
        stations.setdefault(station, [])
        stations[station].append(item_string)

    '''
        lambda function used to generate a string of the form:

        Station Name:
        Menu Item 1 (Label 1, Label 2)
        Menu Item 2
        Menu Item 3 (Label 1)
        ...
    '''
    get_str = lambda station: f"{station}:\n{chr(10).join(sorted(stations[station]))}"

    output = [get_str(station) for station in sorted(stations.keys())]

    return '\n\n'.join(output)


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
            labels = ', '.join(sorted(cor_icon.values())) if cor_icon else ""

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

@FLASK_APP.route('/')
def main_html():
    '''
        creates an HTML file called "DDMMYY.html" with the list of late night
        items if no file was found.
    '''
    try:
        name = generate_name()

        html = open(name).read() if isfile(name) else generate_html_file(name)
        return html

    except Exception as exception:
        print(exception)
        return "<h1>Internal Error.</h1>"

def main_loop():
    '''
        creates the process that refreshes the html file
        every 15 minutes
    '''
    refresh = Process(target=generate_file_every_15_min)
    refresh.start()

main_loop()
