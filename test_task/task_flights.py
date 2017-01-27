import datetime
import json
import requests
import sys

from lxml import html


def get_flights(departure, destination, date_out, date_back=None):
    """Request data about flights"""
    with requests.Session() as session:
        url = 'http://www.flyniki.com/en/start.php'
        if date_back:
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
            'returnDate':  date_back,
            'adultCount': 1,
            'oneway': one_way,
            'market': market_value[0],
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
            response1 = session.post(response.url, data=trip_data, verify=False)
            response2 = session.post(response1.url, data=ajax_trip_data, verify=False)
        except requests.exceptions.ConnectTimeout:
            print "Connection Timeout occurred"
        except requests.exceptions.ConnectionError:
            print "Connection Error occurred"
        except requests.exceptions.HTTPError:
            print "Http Error occurred"
        else:
            return response2


def check_date(date_out, date_back=None):
    """Check if a date is correct"""
    today = datetime.date.today()
    if not date_back:
        datetime_return = datetime.datetime.strptime('9999-12-31', '%Y-%m-%d').date()
    else:
        datetime_return = datetime.datetime.strptime(date_back, '%Y-%m-%d').date()
    datetime_out = datetime.datetime.strptime(date_out, '%Y-%m-%d').date()
    if datetime_return >= datetime_out >= today:
        return 1
    else:
        print "Please, check your date"
        return 0


def parse_json(response):
    """Parse file and print results"""
    flight_info_json = json.loads(response.text)
    flight_data = flight_info_json['templates']['main'].replace("\\", "")
    root = html.fromstring(flight_data)
    flight_info_xml = root.xpath('//div[contains(@class, "lowest")]//span')
    departure_list = []
    destination_list = []
    if len(sys.argv) != 4:
        for m in flight_info_xml:
            if m.get('title')[0:3] == sys.argv[1]:
                temp_list1 = [m.get('title'), m.text]
                departure_list.append(temp_list1)
            elif m.get('title')[0:3] == sys.argv[2]:
                temp_list2 = [m.get('title'), m.text]
                destination_list.append(temp_list2)
        for n in range(len(departure_list)):
            for m in range(len(destination_list)):
                print departure_list[n][0], destination_list[m][0],  "Total cost:", \
                    float(departure_list[n][1])+float(destination_list[m][1])
    else:
        for d in flight_info_xml:
            print d.get('title')


def scrape():
    """Start all functions"""
    departure = sys.argv[1]
    destination = sys.argv[2]
    date_out = sys.argv[3]
    if len(sys.argv) == 4:
        date_back = None
    else:
        date_back = sys.argv[4]
    if check_date(date_out, date_back):
        result_json = get_flights(departure, destination, date_out, date_back)
        if result_json:
            parse_json(result_json)

if __name__ == '__main__':
    scrape()

