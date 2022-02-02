import sys
from datetime import date
import json

try:
    import requests
except ImportError:
    print('\nrequests module not installed. Run: pip install requests')
    sys.exit()

try:
    from bs4 import BeautifulSoup
except ImportError:
    print('\nbs4 module not installed. Run: pip install bs4')
    sys.exit()

try:
    import sqlite3
except ImportError:
    print('\nsqlite3 module not installed. Run: pip install sqlite3')
    sys.exit()

START_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/96.0.4664.110 Safari/537.36'
                 }

s = requests.Session()


def get_csrf_token():
    r = s.get("https://www.synevo.ua/ua/tests", headers=START_HEADERS)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        # csrf = soup.findall('meta', name='csrf-token')
        csrf = soup.find("meta", attrs={'name': 'csrf-token'})
        return csrf["content"]
        # print(print(csrf["content"] if csrf else "No meta title given"))
    else:
        print('Error get page https://www.synevo.ua/ua/tests')


def get_tests_all_loc():
    cities = []
    csrf = get_csrf_token()
    if csrf is None:
        print('Error csrf token')
        sys.exit()
    conn = sqlite3.connect('testlabs.db')
    sqlq = '''SELECT citycode FROM cityes_synevo WHERE
        parsing_date = '{today}';'''.format(today=date.today())
    cursor = conn.execute(sqlq)
    result_list = cursor.fetchall()
    for j in range(len(result_list)):
        cities.append(result_list[j][0])
    conn.close()
    for city in cities:
        get_tests_by_loc(csrf, city)


def get_tests_by_loc(csrf, location=152):
    data = {"location_id": location}
    headers = {'X-CSRF-TOKEN': csrf,
               'sec-ch-ua-mobile': '?0',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/96.0.4664.110 Safari/537.36',
               'Referer': 'https://www.synevo.ua/ua/tests',
               }
    print(f'Loading data to tmp_txt/synevo_tests_by_loc_{location}.txt: Start')
    r = s.post('https://www.synevo.ua/api/test/tests-by-loc', headers=headers, data=data)
    if r.status_code == 200:
        with open(f'tmp_txt/synevo_tests_by_loc_{location}.txt', 'w', encoding='UTF-8') as file:
            file.write(r.text)
        print(f'Loading data to tmp_txt/synevo_tests_by_loc_{location}.txt: Done')
        get_test(location)
    else:
        print('Error get page https://www.synevo.ua/api/test/tests-by-loc')


def get_test(citycode):
    print(f'Loading data tests region {citycode} to DB: Start')
    f = open(f'tmp_txt/synevo_tests_by_loc_{citycode}.txt', 'r', encoding='UTF-8')
    data = json.loads(f.read())

    if len(data['json']) < 1:
        print(f'\nEmpty data in synevo_tests_by_loc_{citycode}.txt')
        sys.exit()
    conn = sqlite3.connect('testlabs.db')
    sqlstr = '''DELETE FROM tests_synevo WHERE
    parsing_date = '{today}' and citycode = '{citycode}';'''.format(today=date.today(), citycode=citycode)
    conn.execute(sqlstr)
    conn.commit()

    for key in data['json']:
        for iter_group in data['json'][key]:
            sqlstr = '''INSERT INTO tests_synevo (
            citycode,
            location_id,
            allow_buy,
            test_category_id,
            test_code,
            test_name_ua,
            test_name_ru,
            price,
            term
            )
                                VALUES ('{citycode}',
                        '{location_id}',
                        '{allow_buy}',
                        '{test_category_id}',
                        '{test_code}',
                        '{test_name_ua}',
                        '{test_name_ru}',
                        '{price}',
                        '{term}');'''.format(
                citycode=citycode,
                location_id=iter_group['location_id'],
                allow_buy=iter_group['allow_buy'],
                test_category_id=key,
                test_code=iter_group['code'],
                test_name_ua=check_string(iter_group['name_ua']),
                test_name_ru=check_string(iter_group['name_ru']),
                price=iter_group['price'],
                term=iter_group['term']
            )
            conn.execute(sqlstr)
            conn.commit()
    conn.close()
    print(f'Loading data tests region {citycode} to DB: Done')


def get_address():
    r = requests.get("https://www.synevo.ua/ua/centers")
    if r.status_code == 200:
        print('Loading city synevo to DB: Start')
        soup = BeautifulSoup(r.text, 'html.parser')
        citi = soup.find("select", class_="control control--select page_location location_list")
        if len(citi.find_all('option')) < 1:
            print('\nEmpty data in var citi')
            sys.exit()
        conn = sqlite3.connect('testlabs.db')
        sqlstr = '''DELETE FROM cityes_synevo WHERE
        parsing_date = '{today}';'''.format(today=date.today())
        conn.execute(sqlstr)
        conn.commit()

        for option in citi.find_all('option'):
            sqlstr = '''INSERT INTO cityes_synevo(citycode,city,region)
            VALUES('{citycode}','{city}','{region}');'''.format(
                citycode=option['value'],
                city=check_string(option.text),
                region=check_string(option['data-region'])
            )
            conn.execute(sqlstr)
            conn.commit()
        print('Loading city synevo to DB: Done')
        print('Loading address synevo to DB: Start')
        labs_list_main = soup.find("ul", class_="labs__list__content tabs__content active")
        labs_list = labs_list_main.find_all("li", class_="labs__list__item")
        if len(labs_list) < 1:
            print('\nEmpty data in var labs_list')
            sys.exit()

        sqlstr = '''DELETE FROM addresses_synevo WHERE
                parsing_date = '{today}';'''.format(today=date.today())
        conn.execute(sqlstr)
        conn.commit()

        for labs_list_item in labs_list:
            city = labs_list_item.find("span", class_="labs__list__city").get_text(strip=True)
            address = labs_list_item.find("span", class_="labs__list__address").get_text(strip=True)
            gps_lon = labs_list_item.find("div", class_="labs__list__location").get("data-center-coordinates-lg")
            gps_lat = labs_list_item.find("div", class_="labs__list__location").get("data-center-coordinates-lt")
            resposm = osm(str(gps_lat) + ',' + str(gps_lon))
            region_list = resposm.split(',')
            region = region_list[-3] if 3 < len(region_list) else 'Empty'
            sqlstr = '''INSERT INTO addresses_synevo(gps_lat, gps_lon, region, osm, city_uk, address_uk)
            VALUES('{gps_lat}', '{gps_lon}', '{region}', '{osm}', '{city_uk}', '{address_uk}'
            );'''.format(
                gps_lat=gps_lat,
                gps_lon=gps_lon,
                region=check_string(region),
                osm=check_string(resposm),
                city_uk=check_string(city),
                address_uk=check_string(address))
            conn.execute(sqlstr)
            conn.commit()
        conn.close()
        print('Loading address synevo to DB: Done')
    else:
        print('Error get page https://www.synevo.ua/ua/centers')


def check_string(string):
    if string is not None:
        return str(string).replace("'", "''")


def osm(coordinates):
    overpass_url = "https://nominatim.openstreetmap.org/search?q={gps}]&format=json".format(gps=coordinates)
    response = requests.get(overpass_url)
    data = response.json()
    return data[0]['display_name']


def main():
    # print(get_csrf_token())
    # get_tests_by_loc(get_csrf_token(), 38)
    get_address()
    get_tests_all_loc()
    #get_test(38)


if __name__ == '__main__':
    main()

