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
            '_ajax[templates][.]': 'priceoverview',
            '_ajax[templates]["]': 'infos',
            '_ajax[templates][/]': 'flightinfo',
            '_ajax[requestParams][departure]': departure,
            '_a jax[requestParams][destination]': destination,
            '_ajax[requestParams][outboundDate]': date_out,
            '_ajax[requestParams][returnDate]': date_back,
            '_ajax[requestParams][adultCount]': 1,
            '_ajax[requestParams][openDateOverview]': '',
            '_ajax[requestParams][oneway]': one_way}
        date_trip_data = {
            '_ajax[templates][]': 'dateoverview'}
        try:
            response1 = session.post(response.url, data=trip_data, verify=False)
            response2 = session.post(response1.url, data=ajax_trip_data, verify=False)
            response3 = session.post(response2.url, data=date_trip_data, verify=False)
        except requests.exceptions.ConnectTimeout:
            print 'Connection Timeout occurred'
        except requests.exceptions.ConnectionError:
            print 'Connection Error occurred'
        else:
            return response2, response3


def check_date(date_out, date_back=None):
    """Check date value"""
    if not check_date_format(date_out, date_back):
        return False
    today = datetime.date.today()
    datetime_return = datetime.datetime.strptime(date_back or '9999-12-31', '%Y-%m-%d').date()
    datetime_out = datetime.datetime.strptime(date_out, '%Y-%m-%d').date()
    if datetime_return >= datetime_out >= today:
        return True
    else:
        print 'Please, check your date'
        return False


def check_date_format(date_out, date_back=None):
    """Check date format"""
    try:
        datetime.datetime.strptime(date_out, '%Y-%m-%d')
        if date_back is not None:
            datetime.datetime.strptime(date_back, '%Y-%m-%d')
    except ValueError:
        print 'Incorrect date format, should be YYYY-MM-DD'
        return False
    else:
        return True


def check_code(departure, destination):
    """Check iata-codes format"""
    if len(departure) != 3 or not departure.isalpha():
        print 'Check your departure code'
        return False
    elif len(destination) != 3 or not destination.isalpha():
        print 'Check your destination code'
        return False
    else:
        return True


def parse_json(response):
    """Parse file"""
    flight_info_json = json.loads(response.text)
    flight_data = flight_info_json['templates']['main'].replace('\\', '')
    price_data = flight_info_json['templates']['priceoverview'].replace('\\', '')
    root1 = html.fromstring(flight_data)
    root2 = html.fromstring(price_data)
    flight_info_xml = root1.xpath('//div[contains(@class, "lowest")]//span')
    currency_charge_xml = root2.xpath('//tr[contains(@class, "additionals-tsc")]'
                                      '//td[contains(@class, "price")]//text()')
    currency = currency_charge_xml[0][1:2]
    charge = currency_charge_xml[0][2:6]
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
            'price': flight_info.text,
            'currency': currency,
            'payment_charge': charge}
        flight_dicts.append(flight_dict)
    return flight_dicts


def print_flights(flight_dicts, one_way):
    """Print flights data"""
    departure = flight_dicts[0]['direction'][0:3]
    destination = flight_dicts[0]['direction'][4:7]
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
                  outbound_flight['duration'], outbound_flight['price_type'], outbound_flight['currency']
            print 'Inbound flight:', inbound_flight['direction'], inbound_flight['time'], \
                  inbound_flight['duration'], inbound_flight['price_type'], inbound_flight['currency']
            print 'Total cost:', float(inbound_flight['price']) + float(outbound_flight['price']) + \
                  float(outbound_flight['payment_charge']), inbound_flight['currency']
            print
    else:
        for flight_info in flight_dicts:
            print 'Outbound flight:', flight_info['direction'], flight_info['time'], \
                flight_info['duration'], flight_info['price_type'], flight_info['currency'],\
                'Total cost:', float(flight_info['price']) + float(flight_info['payment_charge']),\
                flight_info['currency']


def scrape():
    """Start all functions"""
    departure = sys.argv[1]
    destination = sys.argv[2]
    date_out = sys.argv[3]
    one_way = len(sys.argv) == 4
    date_back = None if one_way else sys.argv[4]
    if not check_date(date_out, date_back) or not check_code(departure, destination):
        # if any of check functions returns False, it also prints error message
        return 0
    result_json = get_flights(departure, destination, date_out, date_back)
    if not result_json:
        # if get_flights function returns None, it also prints error message
        return 0
    try:
        result_dicts = parse_json(result_json[0])
        print_flights(result_dicts, one_way)
    except (SyntaxError, KeyError):
        check_for_errors(result_json)


def check_for_errors(result_json):
    """Print error messages"""
    flight_info_json = json.loads(result_json[1].text)
    if 'error' in flight_info_json:
        flight_data = flight_info_json['error'].replace('\\', '')
        root = html.fromstring(flight_data)
        error_info = root.xpath('//div[contains(@class, "entry")]//p//text()')
        print error_info[0]
    else:
        flight_data = flight_info_json['templates']['dateoverview'].replace('\\', '')
        root = html.fromstring(flight_data)
        error_info = root.xpath('//div[contains(@class, "wrapper")]//p//text()')
        print error_info[3]


if __name__ == '__main__':
    scrape()

