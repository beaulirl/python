import re
# import requests


def list_init(fn):
    def wrapped(*args):
        list_flights = []
        for flight in fn(*args):
            origin = flight[0]
            destination = flight[1]
            dict_flight = {"from": origin, "to": destination, "mode": "flight"}
            list_flights.append(dict_flight)
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
    results = []
    for string in strings:
        airports = iter(re.findall(r'(\w\w\w):', string))
        origin = next(airports)
        for destination in airports:
            results.append((origin, destination))
    return results


read_function()
