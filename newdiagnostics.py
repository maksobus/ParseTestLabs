import sys
import json
from datetime import date

try:
    import brotli
except ImportError:
    print('\nbrotli module not installed. Run: pip install brotli')
    sys.exit()

try:
    import sqlite3
except ImportError:
    print('\nrequests module not installed. Run: pip install sqlite3')
    sys.exit()

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
    r = s.get("https://newdiagnostics.ua/", headers=START_HEADERS)
    if r.status_code == 200:
        return r.headers
    else:
        print('Error get page https://newdiagnostics.ua/')


def get_tests():
    print('Loading data to tmp_txt/tests_by_newdiagnostics.txt: Start')
    headers = {
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/96.0.4664.110 Safari/537.36'
                }
    r = s.get('https://newdiagnostics.ua/ua/vracham/analizyi-i-czenyi', headers=headers)
    if r.status_code == 200:
        with open('tmp_txt/tests_by_newdiagnostics.txt', 'w', encoding='UTF-8') as file:
            file.write(r.text)
        print('Loading data to tmp_txt/tests_by_newdiagnostics.txt: Done')
    else:
        print('Error get page https://newdiagnostics.ua/ua/vracham/analizyi-i-czenyi')
        sys.exit()
    print('Loading data tests to DB: Start')
    conn = sqlite3.connect('testlabs.db')
    sqlstr = '''DELETE FROM tests_newdiagnostics WHERE
    parsing_date = '{today}';'''.format(today=date.today())
    conn.execute(sqlstr)
    conn.commit()
    f = open('tmp_txt/tests_by_newdiagnostics.txt', 'r', encoding='UTF-8')
    soup = BeautifulSoup(f.read(), 'html.parser')
    main_group = soup.find("div", class_="list-sp")
    main_group_test = main_group.find_all("div", class_="item")
    for item_group in main_group_test:
        test_category = item_group.find("div", class_="def-link").get_text(strip=True)
        items1 = item_group.find_all("div", class_="service row")
        items2 = item_group.find_all("div", class_="service3 row")
        if len(items1) > 0:
            for item in items1:
                code = item.find("span").get_text(strip=True)
                test_name = item.find("a").get_text(strip=True)
                price_term = item.find("p").get_text()
                price_term_split = price_term.split("грн.")
                sqlstr = '''INSERT INTO tests_newdiagnostics
                (test_category, test_code, test_name, price, term)
                VALUES('{test_category}', '{test_code}', '{test_name}', '{price}', '{term}');'''.format(
                    test_category=check_string(test_category),
                    test_code=check_string(code),
                    test_name=check_string(test_name),
                    price=check_string(price_term_split[0].replace("Ціна: ", "")),
                    term=check_string(price_term_split[1].replace("Термін виконання, днів: ", ""))
                )
                conn.execute(sqlstr)
                conn.commit()
        if len(items2) > 0:
            for item in items2:
                code = item.find("p", class_="sTitleOuter").find(text=True)
                test_name = item.find("a").get_text(strip=True)
                div = item.find("div", class_="col-sm-6")
                children = div.findChildren()
                price_term = children[2].get_text()
                price_term_split = price_term.split("грн.")
                sqlstr = '''INSERT INTO tests_newdiagnostics
                (test_category, test_code, test_name, price, term)
                VALUES('{test_category}', '{test_code}', '{test_name}', '{price}', '{term}');'''.format(
                    test_category=check_string(test_category),
                    test_code=check_string(code),
                    test_name=check_string(test_name),
                    price=check_string(price_term_split[0].replace("Ціна: ", "")),
                    term=check_string(price_term_split[1].replace("Термін виконання, днів:", ""))
                )
                conn.execute(sqlstr)
                conn.commit()
    conn.close()
    print('Loading data tests to DB: Done')


def get_address():
    print('Loading data to tmp_txt/newdiagnostics_getLoc.txt: Start')
    headers = {'accept': 'application/json, text/javascript, */*; q=0.01',
               'accept-encoding': 'gzip, deflate, br',
               'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
               'referer': 'https://newdiagnostics.ua/',
               'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
               'sec-ch-ua-mobile': '?0',
               'sec-ch-ua-platform': '"Windows"',
               'sec-fetch-dest': 'empty',
               'sec-fetch-mode': 'cors',
               'sec-fetch-site': 'same-origin',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/96.0.4664.110 Safari/537.36',
               'x-requested-with': 'XMLHttpRequest'}
    r = s.get('https://newdiagnostics.ua/ajax?action=getLoc', headers=headers)
    if r.status_code == 200:
        with open('tmp_txt/newdiagnostics_getLoc.txt', 'w', encoding='UTF-8') as file:
            file.write(r.text)
        print('Loading data to tmp_txt/newdiagnostics_getLoc.txt: Done')
    else:
        print('Error get page https://newdiagnostics.ua/ajax?action=getLoc')


def load_address_to_sql():
    print('Loading address newdiagnostics to DB: Start')
    f = open('tmp_txt/newdiagnostics_getLoc.txt', 'r', encoding='UTF-8')
    data = json.loads(f.read())
    if len(data["data"]) < 1:
        print('\nEmpty data in newdiagnostics_getLoc.txt')
        sys.exit()

    conn = sqlite3.connect('testlabs.db')
    sqlstr = '''DELETE FROM addresses_newdiagnostics WHERE
    parsing_date = '{today}';'''.format(today=date.today())
    conn.execute(sqlstr)
    conn.commit()

    for address in data["data"]:
        gps = address['gps'].split(',')
        resposm = osm(address['gps'])
        region_list = resposm.split(',')
        region = region_list[-3] if 3 < len(region_list) else 'Empty'
        sqlstr = '''INSERT INTO addresses_newdiagnostics ( active, address_ru, address_uk, city_ru, city_uk, osm, 
        region, gps_lon, gps_lat, migx_id ) VALUES ('{active}','{address_ru}','{address_uk}','{city_ru}','{city_uk}',
        '{osm}', '{region}','{gps_lon}','{gps_lat}','{migx}' );'''.format(
            active=address['active'],
            address_ru=check_string(address['adress_ru']),
            address_uk=check_string(address['adress_uk']),
            city_ru=check_string(address['city_ru']),
            city_uk=check_string(address['city_uk']),
            osm=check_string(resposm),
            region=check_string(region),
            gps_lon=gps[0].strip(),
            gps_lat=gps[1].strip(),
            migx=address['MIGX_id']
        )

        conn.execute(sqlstr)
        conn.commit()
    conn.close()
    print('Loading address newdiagnostics to DB: Done')


def check_string(string):
    if string is not None:
        return str(string).replace("'", "''")


def osm(coordinates):
    overpass_url = "https://nominatim.openstreetmap.org/search?q={gps}]&format=json".format(gps=coordinates)
    response = requests.get(overpass_url)
    data = response.json()
    return data[0]['display_name']


def main():
    # get_csrf_token()
    # get_address()
    # load_address_to_sql()
    get_tests()


if __name__ == '__main__':
    main()

