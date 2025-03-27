from persistent import Persistent
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional
from abc import ABC, abstractmethod

class BaseModel(Persistent, ABC):
    """Classe base para todos os modelos"""
    @abstractmethod
    def validate(self) -> bool:
        """Valida os dados do modelo"""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"

class Pessoa(BaseModel):
    """Classe base para pessoas"""
    __slots__ = ['id', 'nome', 'cpf', 'email', '_validated']

    def __init__(self, id: int, nome: str, cpf: str, email: str):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self._validated = False
        self.validate()

    def validate(self) -> bool:
        if not all([self.nome, self.cpf, self.email]):
            raise ValueError("Todos os campos são obrigatórios")
        if not len(self.cpf) == 11:
            raise ValueError("CPF deve ter 11 dígitos")
        if '@' not in self.email:
            raise ValueError("Email inválido")
        self._validated = True
        return True

class Usuario(Pessoa):
    """Modelo de usuário"""
    __slots__ = ['numero_cartao', 'ativo']

    def __init__(self, id: int, nome: str, cpf: str, email: str, numero_cartao: str):
        self.numero_cartao = numero_cartao
        self.ativo = True
        super().__init__(id, nome, cpf, email)

    def validate(self) -> bool:
        super().validate()
        if not self.numero_cartao:
            raise ValueError("Número do cartão é obrigatório")
        return True

class Funcionario(Pessoa):
    """Modelo de funcionário"""
    __slots__ = ['matricula', 'cargo']

    def __init__(self, id: int, nome: str, cpf: str, email: str, matricula: str, cargo: str):
        self.matricula = matricula
        self.cargo = cargo
        super().__init__(id, nome, cpf, email)

    def validate(self) -> bool:
        super().validate()
        if not all([self.matricula, self.cargo]):
            raise ValueError("Matrícula e cargo são obrigatórios")
        return True

class Livro(BaseModel):
    """Modelo de livro"""
    __slots__ = ['id', 'titulo', 'autor', 'isbn', 'disponivel']

    def __init__(self, id: int, titulo: str, autor: str, isbn: str):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.isbn = isbn
        self.disponivel = True
        self.validate()

    def validate(self) -> bool:
        if not all([self.titulo, self.autor, self.isbn]):
            raise ValueError("Todos os campos são obrigatórios")
        if not len(self.isbn) in [10, 13]:
            raise ValueError("ISBN deve ter 10 ou 13 dígitos")
        return True

class Emprestimo(BaseModel):
    """Modelo de empréstimo"""
    __slots__ = ['id', 'usuario', 'livro', 'data_emprestimo', 
                 'data_devolucao', 'devolvido', '_p_changed']

    def __init__(self, id: int, usuario: Usuario, livro: Livro):
        self.id = id
        self.usuario = usuario
        self.livro = livro
        self.data_emprestimo = datetime.now()
        self.data_devolucao = self.data_emprestimo + timedelta(days=14)
        self.devolvido = False
        self.validate()
        self._emprestar_livro()

    def validate(self) -> bool:
        if not self.usuario.ativo:
            raise ValueError("Usuário inativo não pode realizar empréstimos")
        if not self.livro.disponivel:
            raise ValueError("Livro não está disponível")
        return True

    def _emprestar_livro(self) -> None:
        """Marca o livro como emprestado"""
        self.livro.disponivel = False
        self._p_changed = True

    def devolver(self) -> None:
        """Processa a devolução do livro"""
        self.devolvido = True
        self.livro.disponivel = True
        self._p_changed = True

    @property
    def esta_atrasado(self) -> bool:
        """Verifica se o empréstimo está atrasado"""
        return not self.devolvido and datetime.now() > self.data_devolucao