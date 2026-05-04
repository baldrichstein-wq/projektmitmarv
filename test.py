import sqlite3
conn = sqlite3.connect('example.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS stocks
             (date text, transaction text, symbol text, qty real, price real)''')
c.execute("INSERT INTO stocks VALUES ('2024-06-01','BUY','AAPL',100,150.00)")
conn.commit()
for row in c.execute('SELECT * FROM stocks'):
    print(row)
conn.close()