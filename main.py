import os
import glob


def temp_folder():
    os.makedirs('tmp_txt', exist_ok=True)
    files = glob.glob('tmp_txt/*')
    for f in files:
        os.remove(f)


def main():
    print('START PARSING')
    import synevo
    import newdiagnostics
    import esculab
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


if __name__ == '__main__':
    temp_folder()
    main()

# http://jsonviewer.stack.hu/
