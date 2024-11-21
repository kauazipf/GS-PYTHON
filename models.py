from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date

# Model para Carros
class Carro(BaseModel):
    id: Optional[int] = Field(default=None, description="Identificador único do carro")
    nome: str = Field(..., description="Nome do carro")
    marca: str = Field(..., description="Marca do carro")
    ano: int = Field(..., ge=1900, description="Ano de fabricação do carro")
    cor: str = Field(..., description="Cor do carro")
    disponivel: Optional[bool] = Field(default=True, description="Disponibilidade do carro para aluguel")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "nome": "Civic",
                "marca": "Honda",
                "ano": 2022,
                "cor": "Preto",
                "disponivel": True
            }
        }

# Model para Clientes
class Cliente(BaseModel):
    id: Optional[int] = Field(default=None, description="Identificador único do cliente")
    nome: str = Field(..., min_length=2, description="Nome completo do cliente")
    email: EmailStr = Field(..., description="Endereço de email válido do cliente")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "nome": "João Silva",
                "email": "joao.silva@example.com"
            }
        }

# Model para Aluguéis
class Aluguel(BaseModel):
    id: Optional[int] = Field(default=None, description="Identificador único do aluguel")
    carro_id: int = Field(..., description="ID do carro a ser alugado")
    cliente_id: int = Field(..., description="ID do cliente que está alugando o carro")
    data_inicio: date = Field(..., description="Data de início do aluguel (YYYY-MM-DD)")
    data_fim: date = Field(..., description="Data de término do aluguel (YYYY-MM-DD)")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "carro_id": 1,
                "cliente_id": 1,
                "data_inicio": "2024-01-01",
                "data_fim": "2024-01-07"
            }
        }
