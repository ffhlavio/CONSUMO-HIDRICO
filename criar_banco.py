import sqlite3

con = sqlite3.connect('database/banco.db')
cur = con.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    telefone TEXT NOT NULL,
    cep TEXT NOT NULL,
    cidade TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

con.commit()
con.close()

print("Banco criado com sucesso.")
