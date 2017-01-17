import requests
from lxml import html
import json


def get_flights(departure, destination, date_out, *args):
    with requests.Session() as c:
        url = 'http://www.flyniki.com/en/start.php'
        oneway = get_way(args)
        trip_data = dict(departure=departure,
                         destination=destination, outboundDate=date_out, returnDate=args, adultCount=1,
                         oneway=oneway, market='US', language='en')
        ajax_trip_data = {
            '_ajax[templates][]': 'main',
            '_ajax[requestParams][departure]': departure,
            '_ajax[requestParams][destination]': destination,
            '_ajax[requestParams][outboundDate]': date_out,
            '_ajax[requestParams][returnDate]': args,
            '_ajax[requestParams][adultCount]': 1,
            '_ajax[requestParams][oneway]': oneway}
        try:
            response1 = c.post(url, data=trip_data, verify=False)
            response2 = c.post(response1.url, data=ajax_trip_data, verify=False)
            parse_json(response2)
        except requests.exceptions.ConnectTimeout:
            print "Connection Timeout occured"
        except requests.exceptions.ConnectionError:
            print "Connection Error occured"
        except requests.exceptions.HTTPError:
            print "Http Error occured"


def get_way(args):
    if args == ():
        return 1
    else:
        return 0


def parse_json(response):
    flight_info_json = json.loads(response.text)
    flight_data = flight_info_json['templates']['main'].replace("\\", "")
    root = html.fromstring(flight_data)
    flight_info_xml = root.xpath('//span[@title]/@title')
    flights_list = []
    for n in flight_info_xml:
        if n not in flights_list:
            flights_list.append(n)
    for m in flights_list:
        print m


if __name__ == '__main__':
    print(get_flights('VCE', 'STR', '2017-02-13'))



