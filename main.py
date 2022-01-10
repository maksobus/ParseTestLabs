def main():
    import synevo
    import newdiagnostics
    synevo.get_address()
    synevo.get_tests_by_loc(synevo.get_csrf_token(), 38)
    newdiagnostics.get_address()
    newdiagnostics.load_address_to_sql()
    newdiagnostics.get_tests()

if __name__ == '__main__':
    main()


#http://jsonviewer.stack.hu/