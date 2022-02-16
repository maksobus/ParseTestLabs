import os
import glob
import synevo
import newdiagnostics
import esculab
import userdef as udf


def temp_folder():
    os.makedirs('tmp_txt', exist_ok=True)
    files = glob.glob('tmp_txt/*')
    for f in files:
        os.remove(f)


def main():
    try:
        print('START PARSING')
        udf.sendmessbot('START PARSING')
        synevo.get_address()
        synevo.get_tests_all_loc()
        newdiagnostics.get_address()
        newdiagnostics.load_address_to_sql()
        newdiagnostics.get_tests()
        esculab.get_cityes()
        esculab.get_address()
        esculab.load_address_to_sql()
        esculab.get_tests_all_loc()
        print('PARSING DONE')
        udf.sendmessbot('PARSING DONE')
    except Exception as e:
        print(e.__class__)
        udf.sendmessbot(f'Error parsing: {e.__class__}')


if __name__ == '__main__':
    temp_folder()
    main()

# http://jsonviewer.stack.hu/
