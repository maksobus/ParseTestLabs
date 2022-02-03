import sys
import shutil

try:
    import sqlite3
except ImportError:
    print('\nsqlite3 module not installed. Run: pip install sqlite3')
    sys.exit()

shutil.copy('testlabs.db', '/home/odmin/Документы/copy_base/testlabs.db')

conn = sqlite3.connect('testlabs.db')

sql_command = ['DELETE FROM addresses_esculab;',
               'DELETE FROM addresses_newdiagnostics;',
               'DELETE FROM addresses_synevo;',
               'DELETE FROM cityes_esculab;',
               'DELETE FROM cityes_synevo;',
               'DELETE FROM tests_esculab;',
               'DELETE FROM tests_newdiagnostics;',
               'DELETE FROM tests_synevo;',
               'VACUUM;']

for sqlq in sql_command:
    print(sqlq)
    conn.execute(sqlq)
    conn.commit()
conn.close()
