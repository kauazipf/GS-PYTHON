from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from database import criar_conexao
import sqlite3

app = FastAPI()

# --- SCHEMAS ---
class Carro(BaseModel):
    id: Optional[int]
    nome: str
    marca: str
    ano: int
    cor: str
    disponivel: Optional[bool] = True

class Cliente(BaseModel):
    id: Optional[int]
    nome: str
    email: str

class Aluguel(BaseModel):
    id: Optional[int]
    carro_id: int
    cliente_id: int
    data_inicio: str
    data_fim: str

# --- ROTAS DE CARROS ---
@app.post("/carros/", response_model=Carro)
def criar_carro(carro: Carro):
    conexao = criar_conexao()
    cursor = conexao.cursor()

    try:
        cursor.execute('''
            INSERT INTO carros (nome, marca, ano, cor, disponivel)
            VALUES (?, ?, ?, ?, ?)
        ''', (carro.nome, carro.marca, carro.ano, carro.cor, 1 if carro.disponivel else 0))
        conexao.commit()
        carro.id = cursor.lastrowid
        return carro
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Erro ao criar carro: " + str(e))
    finally:
        conexao.close()

@app.get("/carros/", response_model=List[Carro])
def listar_carros(disponivel: Optional[bool] = None):
    conexao = criar_conexao()
    cursor = conexao.cursor()

    query = "SELECT id, nome, marca, ano, cor, disponivel FROM carros"
    params = []

    if disponivel is not None:
        query += " WHERE disponivel = ?"
        params.append(1 if disponivel else 0)

    cursor.execute(query, params)
    carros = cursor.fetchall()
    conexao.close()

    return [
        Carro(
            id=row[0],
            nome=row[1],
            marca=row[2],
            ano=row[3],
            cor=row[4],
            disponivel=bool(row[5])
        )
        for row in carros
    ]

@app.put("/carros/{carro_id}", response_model=Carro)
def atualizar_carro(carro_id: int, carro: Carro):
    conexao = criar_conexao()
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM carros WHERE id = ?", (carro_id,))
    carro_existente = cursor.fetchone()

    if not carro_existente:
        conexao.close()
        raise HTTPException(status_code=404, detail="Carro não encontrado.")

    cursor.execute('''
        UPDATE carros
        SET nome = ?, marca = ?, ano = ?, cor = ?, disponivel = ?
        WHERE id = ?
    ''', (carro.nome, carro.marca, carro.ano, carro.cor, 1 if carro.disponivel else 0, carro_id))
    conexao.commit()
    conexao.close()
    carro.id = carro_id
    return carro

@app.delete("/carros/{carro_id}")
def deletar_carro(carro_id: int):
    conexao = criar_conexao()
    cursor = conexao.cursor()

    cursor.execute("DELETE FROM carros WHERE id = ?", (carro_id,))
    if cursor.rowcount == 0:
        conexao.close()
        raise HTTPException(status_code=404, detail="Carro não encontrado.")
    conexao.commit()
    conexao.close()
    return {"detail": "Carro deletado com sucesso."}

# --- ROTAS DE CLIENTES ---
@app.post("/clientes/", response_model=Cliente)
def criar_cliente(cliente: Cliente):
    """Cria um novo cliente."""
    conexao = criar_conexao()
    cursor = conexao.cursor()

    try:
        cursor.execute('''
            INSERT INTO clientes (nome, email)
            VALUES (?, ?)
        ''', (cliente.nome, cliente.email))
        conexao.commit()
        cliente.id = cursor.lastrowid
        return cliente
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Erro ao criar cliente: {e}")
    finally:
        conexao.close()


@app.get("/clientes/", response_model=List[Cliente])
def listar_clientes():
    """Lista todos os clientes cadastrados."""
    conexao = criar_conexao()
    cursor = conexao.cursor()

    cursor.execute("SELECT id, nome, email FROM clientes")
    clientes = cursor.fetchall()
    conexao.close()

    return [Cliente(id=row[0], nome=row[1], email=row[2]) for row in clientes]


@app.get("/clientes/{cliente_id}", response_model=Cliente)
def obter_cliente(cliente_id: int):
    """Obtém os detalhes de um cliente pelo ID."""
    conexao = criar_conexao()
    cursor = conexao.cursor()

    cursor.execute("SELECT id, nome, email FROM clientes WHERE id = ?", (cliente_id,))
    cliente = cursor.fetchone()
    conexao.close()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    return Cliente(id=cliente[0], nome=cliente[1], email=cliente[2])


@app.put("/clientes/{cliente_id}", response_model=Cliente)
def atualizar_cliente(cliente_id: int, cliente: Cliente):
    """Atualiza as informações de um cliente."""
    conexao = criar_conexao()
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
    cliente_existente = cursor.fetchone()

    if not cliente_existente:
        conexao.close()
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    cursor.execute('''
        UPDATE clientes
        SET nome = ?, email = ?
        WHERE id = ?
    ''', (cliente.nome, cliente.email, cliente_id))
    conexao.commit()
    conexao.close()
    cliente.id = cliente_id
    return cliente


@app.delete("/clientes/{cliente_id}")
def deletar_cliente(cliente_id: int):
    """Remove um cliente do sistema."""
    conexao = criar_conexao()
    cursor = conexao.cursor()

    cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    if cursor.rowcount == 0:
        conexao.close()
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    conexao.commit()
    conexao.close()
    return {"detail": "Cliente deletado com sucesso."}

# --- ROTAS DE ALUGUÉIS ---
@app.post("/alugueis/", response_model=Aluguel)
def criar_aluguel(aluguel: Aluguel):
    """Cria um novo registro de aluguel."""
    conexao = criar_conexao()
    cursor = conexao.cursor()

    # Verificar se o carro está disponível
    cursor.execute("SELECT disponivel FROM carros WHERE id = ?", (aluguel.carro_id,))
    carro = cursor.fetchone()
    if not carro or carro[0] == 0:
        raise HTTPException(status_code=400, detail="Carro não está disponível para aluguel.")

    # Inserir o aluguel no banco de dados
    cursor.execute('''
        INSERT INTO alugueis (carro_id, cliente_id, data_inicio, data_fim)
        VALUES (?, ?, ?, ?)
    ''', (aluguel.carro_id, aluguel.cliente_id, aluguel.data_inicio, aluguel.data_fim))

    # Atualizar a disponibilidade do carro
    cursor.execute("UPDATE carros SET disponivel = 0 WHERE id = ?", (aluguel.carro_id,))
    conexao.commit()
    aluguel.id = cursor.lastrowid
    conexao.close()
    return aluguel


@app.get("/alugueis/", response_model=List[Aluguel])
def listar_alugueis():
    """Lista todos os aluguéis."""
    conexao = criar_conexao()
    cursor = conexao.cursor()

    cursor.execute("SELECT id, carro_id, cliente_id, data_inicio, data_fim FROM alugueis")
    alugueis = cursor.fetchall()
    conexao.close()

    return [
        Aluguel(
            id=row[0],
            carro_id=row[1],
            cliente_id=row[2],
            data_inicio=row[3],
            data_fim=row[4]
        )
        for row in alugueis
    ]


@app.get("/alugueis/{aluguel_id}", response_model=Aluguel)
def obter_aluguel(aluguel_id: int):
    """Obtém os detalhes de um aluguel pelo ID."""
    conexao = criar_conexao()
    cursor = conexao.cursor()

    cursor.execute("SELECT id, carro_id, cliente_id, data_inicio, data_fim FROM alugueis WHERE id = ?", (aluguel_id,))
    aluguel = cursor.fetchone()
    conexao.close()

    if not aluguel:
        raise HTTPException(status_code=404, detail="Aluguel não encontrado.")

    return Aluguel(
        id=aluguel[0],
        carro_id=aluguel[1],
        cliente_id=aluguel[2],
        data_inicio=aluguel[3],
        data_fim=aluguel[4]
    )


@app.delete("/alugueis/{aluguel_id}")
def deletar_aluguel(aluguel_id: int):
    """Remove um aluguel e libera o carro correspondente."""
    conexao = criar_conexao()
    cursor = conexao.cursor()

    # Verificar se o aluguel existe
    cursor.execute("SELECT carro_id FROM alugueis WHERE id = ?", (aluguel_id,))
    aluguel = cursor.fetchone()
    if not aluguel:
        conexao.close()
        raise HTTPException(status_code=404, detail="Aluguel não encontrado.")

    # Remover o aluguel
    cursor.execute("DELETE FROM alugueis WHERE id = ?", (aluguel_id,))
    # Atualizar a disponibilidade do carro
    cursor.execute("UPDATE carros SET disponivel = 1 WHERE id = ?", (aluguel[0],))
    conexao.commit()
    conexao.close()
    return {"detail": "Aluguel deletado e carro liberado com sucesso."}
