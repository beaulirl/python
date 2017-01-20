import datetime
import json
import requests

from lxml import html


def get_flights(departure, destination, date_out, *args):
    """Request data about flights"""
    if check_date(date_out, *args):
        with requests.Session() as session:
            url = 'http://www.flyniki.com/en/start.php'
            one_way = 1 if not args else 0
            trip_data = {'departure': departure, 'destination': destination, 'outboundDate': date_out,
                         'returnDate':  args, 'adultCount': 1, 'oneway': one_way, 'market': 'US', 'language': 'en'}
            ajax_trip_data = {
                '_ajax[templates][]': 'main',
                '_ajax[requestParams][departure]': departure,
                '_ajax[requestParams][destination]': destination,
                '_ajax[requestParams][outboundDate]': date_out,
                '_ajax[requestParams][returnDate]':  args,
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
            parse_json(response2)


def check_date(date_out, *args):
    """Check if a date is correct"""
    today = datetime.date.today()
    if not args:
        datetime_return = datetime.datetime.strptime('9999-12-31', '%Y-%m-%d')
    else:
        date_return = args[0]
        datetime_return = datetime.datetime.strptime(date_return, '%Y-%m-%d').date()
    datetime_out = datetime.datetime.strptime(date_out, '%Y-%m-%d').date()
    if datetime_out < today or datetime_return < today or datetime_return < datetime_out:
        print "Please, check your date"
        return 0
    else:
        return 1


def parse_json(response):
    """Parse file and print results"""
    flight_info_json = json.loads(response.text)
    flight_data = flight_info_json['templates']['main'].replace("\\", "")
    root = html.fromstring(flight_data)
    flight_info_xml = root.xpath('//span[@title]/@title')
    flights_list = []
    print flight_info_xml[0], "Pounds"
    for k in range(len(flight_info_xml)):
        if k != len(flight_info_xml)-1 and flight_info_xml[k][36:50] != flight_info_xml[k + 1][36:50] and \
                        flight_info_xml[k+1] not in flights_list:
            flights_list.append(flight_info_xml[k+1])
            print flight_info_xml[k+1], "Pounds"

if __name__ == '__main__':
    print get_flights('VCE', 'STR', '2017-02-13', '2017-02-14')
