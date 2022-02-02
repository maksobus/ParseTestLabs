import sys

try:
    import sqlite3
except ImportError:
    print('\nsqlite3 module not installed. Run: pip install sqlite3')
    sys.exit()

conn = sqlite3.connect('testlabs.db')
sqlstr = '''VACUUM;'''
conn.execute(sqlstr)
conn.commit()
conn.close()
