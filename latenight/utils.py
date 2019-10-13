'''
    Fetches a list of food items being served
    at late night.
'''
import json
import re
import requests

# regular expressions used to fetch dictionaries and station names
MENU_ITEMS_REGEX = r"Bamco\.(?:menu_items|dayparts\[\'7\'\]) = ({(?:.+:.+,?)+})"
STATION_REGEX = r"<strong>@?(.+)<\/strong>"
ALT_LABELS = {"Made without Gluten-Containing Ingredients": "Gluten-Free"}

def fetch_from_website():
    req = requests.get("https://vassar.cafebonappetit.com/")

    if req.status_code == 200:
        return req.text
    
    raise Exception("error fetching from deece website")

def parse_menu_items(html):
    menus = re.findall(MENU_ITEMS_REGEX, html)
    if len(menus) == 2:
        menu_items = json.loads(menus[0])
        late_night_menu = json.loads(menus[1])
        
        for area in filter(lambda s: s["label"].startswith("Gordon"), late_night_menu['stations']):
            results = {}

            for item in map(lambda i: menu_items.get(i), area['items']):
                name = item['label']
                cor_icon = item['cor_icon'] or dict()
                labels = ', '.join(map(lambda l: ALT_LABELS.get(l, l), cor_icon.values()))
                station_name = item.get('station', '')[9:-9]
                results.setdefault(station_name, [])
                results[station_name].append({'name': name, 'restrictions': labels})
            return results

    raise Exception("error parsing menu items")

def fetch_menu():
    '''
        makes a GET request to CBA's website and parses HTML
        file to find menu items.
    '''
    html = fetch_from_website()
    return parse_menu_items(html)
