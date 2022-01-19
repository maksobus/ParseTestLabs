import sys
import json
from datetime import date

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

HEADERS = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
               'accept-encoding': 'gzip, deflate, br',
               'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
               'referer': 'https://esculab.com/',
               'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
               'sec-ch-ua-mobile': '?0',
               'sec-ch-ua-platform': '"Windows"',
               'sec-fetch-dest': 'empty',
               'sec-fetch-mode': 'cors',
               'sec-fetch-site': 'same-origin',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/96.0.4664.110 Safari/537.36'
               }

s = requests.Session()


def get_address():
    print('Loading data to tmp_txt/esculab_getLoc.txt: Start')
    r = s.get('https://esculab.com/api/customers/getPunkts', headers=HEADERS)
    if r.status_code == 200:
        with open('tmp_txt/esculab_getLoc.txt', 'w', encoding='UTF-8') as file:
            file.write(r.text)
        print('Loading data to tmp_txt/esculab_getLoc.txt: Done')
    else:
        print('Error get page https://esculab.com/api/customers/getPunkts')


def load_address_to_sql():
    print('Loading address esculab to DB: Start')
    f = open('tmp_txt/esculab_getLoc.txt', 'r')
    data = json.loads(f.read())
    if len(data[0]) < 1:
        print('\nEmpty data in esculab_getLoc.txt')
        sys.exit()

    conn = sqlite3.connect('testlabs.db')
    sqlstr = '''DELETE FROM addresses_esculab WHERE
    parsing_date = '{today}';'''.format(today=date.today())
    conn.execute(sqlstr)
    conn.commit()

    for address in data:
        gps = str(address['lat']) + ',' + str(address['lon'])
        resposm = osm(gps)
        region = resposm.split(',')
        sqlstr = '''INSERT INTO addresses_esculab (address_ru, address_uk, city_uk, osm,
        region, gps_lon, gps_lat, id_Punkt ) VALUES ('{address_ru}','{address_uk}', '{city_uk}',
        '{osm}', '{region}', '{gps_lon}','{gps_lat}','{id_Punkt}' );'''.format(

            address_ru=check_string(address['addressRu']),
            address_uk=check_string(address['address']),
            city_uk=check_string(address['region']),
            osm=check_string(resposm),
            region=check_string(region[-3]),
            gps_lon=address['lon'],
            gps_lat=address['lat'],
            id_Punkt=address['idPunkt']
        )
        conn.execute(sqlstr)
        conn.commit()
    conn.close()
    print('Loading address esculab to DB: Done')


def get_cityes():
    print('Loading data to tmp_txt/esculab_getRegions.txt: Start')
    r = s.get('https://esculab.com/api/customers/getRegions', headers=HEADERS)
    if r.status_code == 200:
        with open('tmp_txt/esculab_getRegions.txt', 'w', encoding='UTF-8') as file:
            file.write(r.text)
        print('Loading data to tmp_txt/esculab_getRegions.txt: Done')
    else:
        print('Error get page https://esculab.com/api/customers/getRegions')
        sys.exit()
    print('Loading city esculab to DB: Start')
    f = open('tmp_txt/esculab_getRegions.txt', 'r')
    data = json.loads(f.read())
    if len(data[0]) < 1:
        print('\nEmpty data in esculab_getRegions.txt')
        sys.exit()
    conn = sqlite3.connect('testlabs.db')
    sqlstr = '''DELETE FROM cityes_esculab WHERE
    parsing_date = '{today}';'''.format(today=date.today())
    conn.execute(sqlstr)
    conn.commit()
    for city in data:
        sqlstr = '''INSERT INTO cityes_esculab (city, city_ru, idReg) 
                VALUES ('{city}','{city_ru}','{idReg}' );'''.format(
            city=check_string(city['name']),
            city_ru=check_string(city['nameRu']),
            idReg=city['idReg']
        )
        conn.execute(sqlstr)
        conn.commit()
    conn.close()
    print('Loading city esculab to DB: Done')


def get_tests_by_loc(location=3204):
    data = {"idreg": location}
    print('Loading data to tmp_txt/getPriceByRegionLocal_' + str(location) + '.txt: Start')
    r = s.post('https://esculab.com/api/customers/getPriceByRegionLocal/ua', headers=HEADERS, data=data)
    print(r.status_code)
    if r.status_code == 200:
        with open('tmp_txt/getPriceByRegionLocal_' + str(location) + '.txt', 'w') as file:
            file.write(r.text)
        print('Loading data to tmp_txt/getPriceByRegionLocal_' + str(location) + '.txt: Done')
    else:
        print('Error get page https://esculab.com/api/customers/getPriceByRegionLocal/ua')


def check_string(string):
    if string is not None:
        return string.replace("'", "''")


def osm(coordinates):
    overpass_url = "https://nominatim.openstreetmap.org/search?q={gps}]&format=json".format(gps=coordinates)
    response = requests.get(overpass_url)
    data = response.json()
    return data[0]['display_name']


def main():
    # get_csrf_token()
    # get_address()
    # load_address_to_sql()
    #get_cityes()
    get_tests_by_loc(4400)
    # get_tests()


if __name__ == '__main__':
    main()