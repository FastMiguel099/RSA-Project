import sqlite3

def create_obu_db():
    try:
        with sqlite3.connect('obu.db') as db:
            db.execute('DROP TABLE IF EXISTS obu')
            db.execute('''
                CREATE TABLE obu(
                    lat REAL,
                    long REAL,
                    ip TEXT PRIMARY KEY
                );
            ''')

            ips = ["192.168.98.20", "192.168.98.30", "192.168.98.40"]
            for ip in ips:
                db.execute('INSERT INTO obu VALUES (NULL, NULL, ?)', (ip,))

            db.commit()
            
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")