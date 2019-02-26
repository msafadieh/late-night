# pylint: disable=pointless-string-statement
'''
    Fetches a list of food items being served
    at late night.
'''
from datetime import datetime
import json
from os.path import isfile
from re import findall
from flask import Flask
from requests import get

# regular expressions used to fetch dictionaries and station names
MENU_ITEMS_REGEX = r"Bamco\.menu_items = ({(?:.+:.+,?)+})"
LATE_NIGHT_REGEX = r"Bamco\.dayparts\[\'7\'\] = ({(?:.+:.+,?)+})"
STATION_REGEX = r"<strong>@?(.+)<\/strong>"

FLASK_APP = Flask('Late Night')

def fetch_menu():
    '''
        makes a GET request to CBA's website and parses HTML
        file to find menu items.
    '''
    req = get('https://vassar.cafebonappetit.com/').text

    menu_data = findall(MENU_ITEMS_REGEX, req)[0]
    menu_items = json.loads(menu_data)

    late_night_data = findall(LATE_NIGHT_REGEX, req)[0]
    late_night_menu = json.loads(late_night_data)

    stations = late_night_menu['stations']
    for station in stations:
        if station['label'] == 'Gordon Commons':
            items = station['items']
            return [menu_items.get(item) for item in items]

    return []

def parse_results(menu):
    '''
        uses the menu items found using the fetch_menu() function
        to generate a well-formatted string (organized by location).
    '''
    stations = dict()

    for item in menu:
        item_name = item.get('label').capitalize()
        labels = ', '.join(sorted(item.get('cor_icon').values()))

        item_string = f"{item_name} ({labels})"
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
    get_string = lambda station: f"{station}:\n{chr(10).join(sorted(stations[station]))}"

    output = [get_string(station) for station in sorted(stations.keys())]

    return '\n\n'.join(output)
    

def parse_as_html(menu):
    stations = dict()

    for item in menu:
        item_name = item.get('label').capitalize()
        labels = ', '.join(sorted(item.get('cor_icon').values()))

        item_string = f"{item_name} ({labels})"
        station = findall(STATION_REGEX, item.get('station'))[0].title()
        stations.setdefault(station, [])
        stations[station].append(item_string)

    string = "<h1>Late Night Menu:</h1>"
    for station in sorted(stations.keys()):
        string += f"<h2>{station}:</h2>"

        sorted_items = sorted(stations[station])
        string += f"<ul>{''.join(f'<li><strong>{item}</strong></li>' for item in sorted_items)}</ul>"

    return string

@FLASK_APP.route('/')
def main_html():
    file_name = f"{datetime.now().strftime('%d%m%y')}.html"

    if isfile(file_name):
        return open(file_name, 'r').read()

    menu = fetch_menu()
    html = parse_as_html(menu)

    with open(file_name, 'w') as file:
        file.write(html)

    return html
