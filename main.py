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
        raise HTTPException(status_code=400, detail="Erro ao criar cliente: " + str(e))
    finally:
        conexao.close()

# --- ROTAS DE ALUGUÉIS ---
@app.post("/alugueis/", response_model=Aluguel)
def criar_aluguel(aluguel: Aluguel):
    conexao = criar_conexao()
    cursor = conexao.cursor()

    cursor.execute("SELECT disponivel FROM carros WHERE id = ?", (aluguel.carro_id,))
    carro = cursor.fetchone()
    if not carro or carro[0] == 0:
        raise HTTPException(status_code=400, detail="Carro não disponível.")

    cursor.execute('''
        INSERT INTO alugueis (carro_id, cliente_id, data_inicio, data_fim)
        VALUES (?, ?, ?, ?)
    ''', (aluguel.carro_id, aluguel.cliente_id, aluguel.data_inicio, aluguel.data_fim))

    cursor.execute("UPDATE carros SET disponivel = 0 WHERE id = ?", (aluguel.carro_id,))
    conexao.commit()
    aluguel.id = cursor.lastrowid
    conexao.close()
    return aluguel
