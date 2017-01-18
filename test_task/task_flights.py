import datetime
import json
import requests

from lxml import html


def get_flights(departure, destination, date_out, *args):
    """This function requests data about flights"""
    with requests.Session() as c:
        url = 'http://www.flyniki.com/en/start.php'
        if check_date(date_out, *args):
            one_way = get_way(args)
            trip_data = dict(departure=departure,
                             destination=destination, outboundDate=date_out, returnDate=args, adultCount=1,
                             oneway=one_way, market='US', language='en')
            ajax_trip_data = {
                '_ajax[templates][]': 'main',
                '_ajax[requestParams][departure]': departure,
                '_ajax[requestParams][destination]': destination,
                '_ajax[requestParams][outboundDate]': date_out,
                '_ajax[requestParams][returnDate]': args,
                '_ajax[requestParams][adultCount]': 1,
                '_ajax[requestParams][oneway]': one_way}
            try:
                response1 = c.post(url, data=trip_data, verify=False)
                response2 = c.post(response1.url, data=ajax_trip_data, verify=False)
                parse_json(response2)
            except requests.exceptions.ConnectTimeout:
                print "Connection Timeout occurred"
            except requests.exceptions.ConnectionError:
                print "Connection Error occurred"
            except requests.exceptions.HTTPError:
                print "Http Error occurred"


def check_date(date_out, *args):
    """This function checks if a date is correct"""
    today = datetime.datetime.now()
    if args == ():
        datetime_return = datetime.datetime.strptime('9999-12-31', '%Y-%m-%d')
    else:
        date_return = args[0]
        datetime_return = datetime.datetime.strptime(date_return, '%Y-%m-%d')
    datetime_out = datetime.datetime.strptime(date_out, '%Y-%m-%d')
    if datetime_out < today or datetime_return < today or datetime_return < datetime_out:
        print("Please, check your date")
        return 0
    else:
        return 1


def get_way(args):
    """This function gives information whether it is one way trip or not"""
    if args == ():
        return 1
    else:
        return 0


def parse_json(response):
    """This function parses file and prints results"""
    flight_info_json = json.loads(response.text)
    flight_data = flight_info_json['templates']['main'].replace("\\", "")
    root = html.fromstring(flight_data)
    flight_info_xml = root.xpath('//span[@title]/@title')
    flights_list = []
    flights_list_new = []
    for n in flight_info_xml:
        if n not in flights_list:
            flights_list.append(n)
    for k in range(len(flights_list)):
        flights_list_new.append(flights_list[k].split(","))
    for index, string in enumerate(flights_list_new):
        if index != len(flights_list_new)-1:
            if flights_list_new[index][3][0:14] == flights_list_new[index+1][3][0:14]:
                flights_list_new.remove(flights_list_new[index + 1])
            print string[1], string[2], string[3], "Pounds"

if __name__ == '__main__':
    print(get_flights('VCE', 'STR', '2017-05-15', '2017-05-17'))
