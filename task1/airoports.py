import re
# import requests
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
    # response = requests.get('https://wl-prod.sabresonicweb.com/SSW2010/static/22/K6K6/170/templates_/__modules/'
    #                         'routes/routesModules.js?1478693573776', verify=False)
    # text = response.text
    with open('18_Full.txt', 'r') as f:
        text = f.read()
    parts = re.findall(r'(\w+:{(?:\w+:\d,)+\w+:\d}[,}])', text)
    for pair in gen(parts):
        print(pair)


@list_init
def gen(strings):
    for string in strings:
        airports = iter(re.findall(r'(\w\w\w):', string))
        origin = next(airports)
        for destination in airports:
            yield origin, destination



read_function()


