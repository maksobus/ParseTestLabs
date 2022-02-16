import parseconfig
import requests
import sys


def check_string(string):
    if string is not None:
        return str(string).replace("'", "''")


def mess_perc(perc):
    sys.stdout.write('\r')
    sys.stdout.flush()
    if perc < 100:
        sys.stdout.write(f"{perc}%")
        sys.stdout.flush()
    else:
        sys.stdout.write(f"{perc}%\n")
        sys.stdout.flush()


def osm(coordinates):
    overpass_url = "https://nominatim.openstreetmap.org/search?q={gps}]&format=json".format(gps=coordinates)
    response = requests.get(overpass_url)
    data = response.json()
    return data[0]['display_name']


def sendmessbot(message_text):
    clear_mess = str(message_text).replace("<", "\\<")
    clear_mess = str(clear_mess).replace(">", "\\>")
    url = f"https://api.telegram.org/bot{parseconfig.TOKEN}/sendMessage?chat_id={parseconfig.CHATID}&parse_mode" \
          f"=MarkdownV2&text={clear_mess} "
    r = requests.post(url)
    if r.status_code == 200:
        pass
    else:
        print('Error send bot message')
        print(r.text)


if __name__ == '__main__':
    pass
