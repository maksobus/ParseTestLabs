import sys
import json
from datetime import date
import userdef as udf

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
    f = open('tmp_txt/esculab_getLoc.txt', 'r', encoding='UTF-8')
    data = json.loads(f.read())
    if len(data[0]) < 1:
        print('\nEmpty data in esculab_getLoc.txt')
        sys.exit()

    conn = sqlite3.connect('testlabs.db')
    sqlstr = '''DELETE FROM addresses_esculab WHERE
    parsing_date = '{today}';'''.format(today=date.today())
    conn.execute(sqlstr)
    conn.commit()
    count_add = 0
    count_all = len(data)
    for address in data:
        count_add += 1
        load_perc = round((count_add/count_all)*100)
        udf.mess_perc(load_perc)
        gps = str(address['lat']) + ',' + str(address['lon'])
        resposm = udf.osm(gps)
        region_list = resposm.split(',')
        region = region_list[-3] if 3 < len(region_list) else 'Empty'
        sqlstr = '''INSERT INTO addresses_esculab (address_ru, address_uk, city_uk, osm,
        region, gps_lon, gps_lat, id_Punkt ) VALUES ('{address_ru}','{address_uk}', '{city_uk}',
        '{osm}', '{region}', '{gps_lon}','{gps_lat}','{id_Punkt}' );'''.format(

            address_ru=udf.check_string(address['addressRu']),
            address_uk=udf.check_string(address['address']),
            city_uk=udf.check_string(address['region']),
            osm=udf.check_string(resposm),
            region=udf.check_string(region),
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
    f = open('tmp_txt/esculab_getRegions.txt', 'r', encoding='UTF-8')
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
            city=udf.check_string(city['name']),
            city_ru=udf.check_string(city['nameRu']),
            idReg=city['idReg']
        )
        conn.execute(sqlstr)
        conn.commit()
    conn.close()
    print('Loading city esculab to DB: Done')


def get_tests_all_loc():
    cities = []
    conn = sqlite3.connect('testlabs.db')
    sqlq = '''SELECT idReg FROM cityes_esculab WHERE
        parsing_date = '{today}';'''.format(today=date.today())
    cursor = conn.execute(sqlq)
    result_list = cursor.fetchall()
    for j in range(len(result_list)):
        cities.append(result_list[j][0])
    conn.close()
    for city in cities:
        get_tests_by_loc(city)


def get_tests_by_loc(location=4400):
    data = {"idreg": str(location)}
    headers = {
        'Host': 'esculab.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/96.0.4664.110 Safari/537.36',
        'accept': 'application/json,text/plain,*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Content-Type': 'application/json;charset=utf-8',
        'Content-Length': '16',
        'Origin': 'https://esculab.com',
        'Connection': 'keep-alive',
        'Referer': 'https://esculab.com/analysis'
    }
    print(f'Loading data to tmp_txt/esculab_getPriceByRegionLocal_{location}.txt: Start')
    r = s.post('https://esculab.com/api/customers/getPriceByRegionLocal/ua', headers=headers, json=data)
    if r.status_code == 200:
        with open(f'tmp_txt/esculab_getPriceByRegionLocal_{location}.txt', 'w', encoding='UTF-8') as file:
            file.write(r.text)
        print(f'Loading data to tmp_txt/esculab_getPriceByRegionLocal_{location}.txt: Done')
        get_test(location)
    else:
        print('Error get page https://esculab.com/api/customers/getPriceByRegionLocal/ua')


def get_test(idregion):
    print(f'Loading data tests region {idregion} to DB: Start')
    f = open(f'tmp_txt/esculab_getPriceByRegionLocal_{idregion}.txt', 'r', encoding='UTF-8')
    data = json.loads(f.read())
    if len(data[0]) < 1:
        print(f'\nEmpty data in esculab_getPriceByRegionLocal_{idregion}.txt')
        sys.exit()
    conn = sqlite3.connect('testlabs.db')
    sqlstr = '''DELETE FROM tests_esculab WHERE
    parsing_date = '{today}' and idReg = '{idReg}';'''.format(today=date.today(), idReg=idregion)
    conn.execute(sqlstr)
    conn.commit()
    count_add = 0
    data_len = len(data)
    for main_group in data:
        count_add += 1
        load_perc = round((count_add / data_len) * 100)
        udf.mess_perc(load_perc)
        for child in main_group["childAnalyzes"]:
            sqlstr = '''INSERT INTO tests_esculab (idReg,
            test_category,
            test_super_category,
            test_code,
            test_name,
            test_price,
            test_discount,
            test_term_day,
            test_term_min,
            test_notSale,
            test_action)
                    VALUES ('{idReg}',
            '{test_category}',
            '{test_super_category}',
            '{test_code}',
            '{test_name}',
            '{test_price}',
            '{test_discount}',
            '{test_term_day}',
            '{test_term_min}',
            '{test_notSale}',
            '{test_action}');'''.format(
                idReg=idregion,
                test_category=udf.check_string(main_group["name"]),
                test_super_category=udf.check_string(main_group["superGroupName"]),
                test_code=udf.check_string(child["code"]),
                test_name=udf.check_string(child["name"]),
                test_price=udf.check_string(child["price"]),
                test_discount=udf.check_string(child["discount"]),
                test_term_day=udf.check_string(child["duration_day"]),
                test_term_min=udf.check_string(child["duration_min"]),
                test_notSale=udf.check_string(child["notSale"]),
                test_action=udf.check_string(child["action"])
            )
            conn.execute(sqlstr)
            conn.commit()
    conn.close()
    print(f'Loading data tests region {idregion} to DB: Done')


def main():
    pass


if __name__ == '__main__':
    main()
