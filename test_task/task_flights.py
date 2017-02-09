"""Get flights data"""
import datetime
import json
import itertools
import sys
import re
import requests

from lxml import html


def get_flights(departure, destination, date_out, date_back=None):
    """Request data about flights"""
    with requests.Session() as session:
        url = 'http://www.flyniki.com/en/start.php'
        if date_back is not None:
            one_way = 0
        else:
            one_way = 1
            date_back = ''
        response = session.get(url)
        root = html.fromstring(response.text)
        market_value = root.xpath('//select[contains(@id, "market")]//option/text()')
        trip_data = {
            'departure': departure,
            'destination': destination,
            'outboundDate': date_out,
            'returnDate': date_back,
            'adultCount': 1,
            'oneway': one_way,
            'market': market_value[0],
            'language': 'en'}
        ajax_trip_data = {
            '_ajax[templates][]': 'main',
            '_ajax[requestParams][departure]': departure,
            '_ajax[requestParams][destination]': destination,
            '_ajax[requestParams][outboundDate]': date_out,
            '_ajax[requestParams][returnDate]': date_back,
            '_ajax[requestParams][adultCount]': 1,
            '_ajax[requestParams][oneway]': one_way}
        try:
            response1 = session.post(response.url, data=trip_data, verify=False)
            response2 = session.post(response1.url, data=ajax_trip_data, verify=False)
        except requests.exceptions.ConnectTimeout:
            print 'Connection Timeout occurred'
        except requests.exceptions.ConnectionError:
            print 'Connection Error occurred'
        else:
            return response2


def check_date(date_out, date_back=None):
    """Check date value"""
    if not check_date_format(date_out, date_back):
        return False
    today = datetime.date.today()
    if date_back is None:
        datetime_return = datetime.datetime.strptime('9999-12-31', '%Y-%m-%d').date()
    else:
        datetime_return = datetime.datetime.strptime(date_back, '%Y-%m-%d').date()
    datetime_out = datetime.datetime.strptime(date_out, '%Y-%m-%d').date()
    if datetime_return >= datetime_out >= today:
        return True
    else:
        print 'Please, check your date'
        return False


def check_date_format(date_out, date_back=None):
    """Check date format"""
    if date_back is None:
        date_back = '9999-12-31'
    try:
        datetime.datetime.strptime(date_out, '%Y-%m-%d')
        datetime.datetime.strptime(date_back, '%Y-%m-%d')
    except ValueError:
        print 'Incorrect date format, should be YYYY-MM-DD'
        return False
    else:
        return True


def check_code(departure, destination):
    """Check iata-codes format"""
    if len(departure) != 3 or not departure.isupper() or not departure.isalpha():
        print 'Check your departure code'
        return False
    elif len(destination) != 3 or not destination.isupper() or not destination.isalpha():
        print 'Check your destination code'
        return False
    else:
        return True


def parse_json(response):
    """Parse file"""
    flight_info_json = json.loads(response.text)
    flight_data = flight_info_json['templates']['main'].replace('\\', '')
    root = html.fromstring(flight_data)
    flight_info_xml = root.xpath('//div[contains(@class, "lowest")]//span')
    flight_dicts = []
    for flight_info in flight_info_xml:
        pattern = r'(\w{3}[-]\w{3})[\s,.]\s(\d{2}[:]\d{2}[-]\d{2}[:]\d{2})' \
                  r'[\s,.]\s(\d{2}\s\w\s\d{2}\s\w+)\s' \
                  r'[\s,.]\s(\w+\s\w+[:]\s\d+[.]\d+)'
        parts = re.match(pattern, flight_info.get('title'))
        flight_dict = {
            'direction': parts.group(1),
            'time': parts.group(2),
            'duration': parts.group(3),
            'price_type': parts.group(4),
            'price': flight_info.text}
        flight_dicts.append(flight_dict)
    return flight_dicts


def print_flights(flight_dicts, departure, destination, one_way):
    """Print flights data"""
    if not one_way:
        outbound_list = []
        inbound_list = []
        for flight_dict in flight_dicts:
            if flight_dict['direction'][0:3] == departure:
                outbound_list.append(flight_dict)
            elif flight_dict['direction'][0:3] == destination:
                inbound_list.append(flight_dict)
        for outbound_flight, inbound_flight in itertools.product(outbound_list, inbound_list):
            print 'Outbound flight:', outbound_flight['direction'], outbound_flight['time'], \
                  outbound_flight['duration'], outbound_flight['price_type']
            print 'Inbound flight:', inbound_flight['direction'], inbound_flight['time'], \
                  inbound_flight['duration'], inbound_flight['price_type']
            print 'Total cost:', float(inbound_flight['price']) + float(outbound_flight['price'])
            print
    else:
        for flight_info in flight_dicts:
            print 'Outbound flight:', flight_info['direction'], flight_info['time'], \
                flight_info['duration'], flight_info['price_type']


def scrape():
    """Start all functions"""
    departure = sys.argv[1]
    destination = sys.argv[2]
    date_out = sys.argv[3]
    one_way = len(sys.argv) == 4
    if one_way:
        date_back = None
    else:
        date_back = sys.argv[4]
    if check_date(date_out, date_back) and check_code(departure, destination):
        result_json = get_flights(departure, destination, date_out, date_back)
        if not result_json:
            return 0
        try:
            result_dicts = parse_json(result_json)
            print_flights(result_dicts, departure, destination, one_way)
        except (SyntaxError, KeyError):
            flight_info_json = json.loads(result_json.text)
            flight_data = flight_info_json['error'].replace('\\', '')
            root = html.fromstring(flight_data)
            error_info = root.xpath('//div[contains(@class, "entry")]//text()')
            print error_info[1]


if __name__ == '__main__':
    scrape()

