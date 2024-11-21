import sqlite3

# Nome do arquivo do banco de dados
DATABASE_NAME = "aluguel_carros.db"

def criar_conexao():
    """Cria uma conexão com o banco de dados."""
    conexao = sqlite3.connect(DATABASE_NAME)
    return conexao

def criar_tabelas():
    """Cria as tabelas no banco de dados se não existirem."""
    conexao = criar_conexao()
    cursor = conexao.cursor()

    # Tabela de Carros
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            marca TEXT NOT NULL,
            ano INTEGER NOT NULL,
            cor TEXT NOT NULL,
            disponivel INTEGER DEFAULT 1
        )
    ''')

    # Tabela de Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    ''')

    # Tabela de Aluguéis
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alugueis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            carro_id INTEGER NOT NULL,
            cliente_id INTEGER NOT NULL,
            data_inicio DATE NOT NULL,
            data_fim DATE NOT NULL,
            FOREIGN KEY (carro_id) REFERENCES carros (id),
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    ''')

    conexao.commit()
    conexao.close()

# Inicializa o banco de dados ao importar o módulo
criar_tabelas()
