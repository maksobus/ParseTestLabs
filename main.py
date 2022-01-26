import os


def temp_folder():
    os.makedirs('tmp_txt', exist_ok=True)


def main():
    import synevo
    import newdiagnostics
    import esculab
    synevo.get_address()
    synevo.get_tests_by_loc(synevo.get_csrf_token(), 38)
    newdiagnostics.get_address()
    newdiagnostics.load_address_to_sql()
    newdiagnostics.get_tests()
    esculab.get_cityes()
    esculab.get_address()
    esculab.load_address_to_sql()


if __name__ == '__main__':
    temp_folder()
    main()

# http://jsonviewer.stack.hu/
