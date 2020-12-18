import sqlite3

try:
    conn = sqlite3.connect('boletos.db')
    print('Conexão realizada com sucesso.')
except:
    print('Conexão falhou')

# FORNECEDORES

action = '''CREATE TABLE IF NOT EXISTS fornecedores
            (
            id_forn INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_forn VARCHAR(255) NOT NULL UNIQUE
            );'''


conn.execute(action)

conn.commit()

# BOLETOS

action = '''CREATE TABLE IF NOT EXISTS boletos
            (
	        id_bole INTEGER PRIMARY KEY AUTOINCREMENT,
	        va_bole FLOAT NOT NULL,
	        st_bole TINYINT NOT NULL,
	        id_forn INTEGER NOT NULL,
	        dt_bole DATETIME NOT NULL,
	        FOREIGN KEY(id_forn) REFERENCES fornecedores(id_forn));'''

conn.execute(action)
conn.commit()
conn.close()
