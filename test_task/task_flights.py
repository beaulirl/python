import datetime
import json
import requests

from lxml import html


def get_flights(departure, destination, date_out, date_back=None):
    """Request data about flights"""
    if not check_date(date_out, date_back):
        return 0
    with requests.Session() as session:
        url = 'http://www.flyniki.com/en/start.php'
        if date_back:
            one_way = 0
        else:
            one_way = 1
            date_back = ''
        trip_data = {
            'departure': departure,
            'destination': destination,
            'outboundDate': date_out,
            'returnDate':  date_back,
            'adultCount': 1,
            'oneway': one_way,
            'market': 'US',
            'language': 'en'}
        ajax_trip_data = {
            '_ajax[templates][]': 'main',
            '_ajax[requestParams][departure]': departure,
            '_ajax[requestParams][destination]': destination,
            '_ajax[requestParams][outboundDate]': date_out,
            '_ajax[requestParams][returnDate]':  date_back,
            '_ajax[requestParams][adultCount]': 1,
            '_ajax[requestParams][oneway]': one_way}
        try:
            response1 = session.post(url, data=trip_data, verify=False)
            response2 = session.post(response1.url, data=ajax_trip_data, verify=False)
        except requests.exceptions.ConnectTimeout:
            print "Connection Timeout occurred"
        except requests.exceptions.ConnectionError:
            print "Connection Error occurred"
        except requests.exceptions.HTTPError:
            print "Http Error occurred"
        return response2


def check_date(date_out, date_back=None):
    """Check if a date is correct"""
    today = datetime.date.today()
    if not date_back:
        datetime_return = datetime.datetime.strptime('9999-12-31', '%Y-%m-%d').date()
    else:
        datetime_return = datetime.datetime.strptime(date_back, '%Y-%m-%d').date()
    datetime_out = datetime.datetime.strptime(date_out, '%Y-%m-%d').date()
    if datetime_return < datetime_out < today :
        print "Please, check your date"
        return 0
    else:
        return 1


def parse_json(response):
    """Parse file and print results"""
    flight_info_json = json.loads(response.text)
    flight_data = flight_info_json['templates']['main'].replace("\\", "")
    root = html.fromstring(flight_data)
    flight_info_xml = root.xpath('//div[contains(@class, "lowest")]//span/@title')
    for m in flight_info_xml:
        print m, "Pounds"


def scrape():
    result_json = get_flights('VCE', 'STR', '2017-01-21', '2017-01-22')
    if result_json:
        parse_json(result_json)


if __name__ == '__main__':
    scrape()


