import re

import requests
from lxml import html
from classpe import Route


def list_init(fn):
    def wrapped(*args):
        list_flights = []
        for origin, destination in fn(*args):
            route = Route(origin, destination, "flight")
            list_flights.append(route)
        return list_flights
    return wrapped


def read_function():
    address = get_js().attrib['src']
    response = requests.get('https://wl-prod.sabresonicweb.com/SSW2010/K6K6/' + address)
    text = response.text
    parts = re.findall(r'(\w+:{(?:\w+:\d,)+\w+:\d}[,}])', text)
    for pair in gen(parts):
        print(pair)


def get_js():
    response = requests.get('https://wl-prod.sabresonicweb.com/SSW2010/K6K6/webqtrip.html')
    page = html.fromstring(response.content)
    script_url = page.xpath('//script[contains(@src, "routesModules")]')[0]
    return script_url


@list_init
def gen(strings):
    for string in strings:
        airports = iter(re.findall(r'(\w\w\w):', string))
        origin = next(airports)
        for destination in airports:
            yield origin, destination


read_function()
