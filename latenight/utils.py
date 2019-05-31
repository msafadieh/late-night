'''
    Fetches a list of food items being served
    at late night.
'''
import json
import re
import requests

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
    req = requests.get('https://vassar.cafebonappetit.com/').text
    menu_data = re.findall(MENU_ITEMS_REGEX, req)

    if menu_data:
        menu_items = json.loads(menu_data[0])

        late_night_data = re.findall(LATE_NIGHT_REGEX, req)

        if late_night_data:
            late_night_menu = json.loads(late_night_data[0])

            stations = late_night_menu['stations']
            for station in stations:
                if station['label'] == 'Gordon Commons':
                    result = {}
                    for item in (menu_items.get(item) for item in station['items']):
                        item_name = item.get('label').capitalize()
                        coricon = item.get('cor_icon', [])

                        # cor_icon is [] and not {} when empty
                        labels_list = sorted(LABELS_DICT.get(key, coricon[key]) for key in coricon)
                        labels = ', '.join(labels_list)

                        item_string = "{} ({})".format(item_name, labels) if labels else item_name
                        station_name = re.findall(STATION_REGEX, item.get('station'))[0].title()
                        result.setdefault(station_name, [])
                        result[station_name].append(item_string)
                    return result
    return {"No Menu": ["Please come back later!"]}
