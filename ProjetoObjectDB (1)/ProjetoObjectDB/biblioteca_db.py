from ZODB import FileStorage, DB
from BTrees.OOBTree import OOBTree
from ZODB.DemoStorage import DemoStorage
import transaction
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
import os
import tempfile
from functools import lru_cache
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BibliotecaDB:
    def __init__(self, filename: str = 'biblioteca.fs'):
        # Define tabelas fora do bloco try/except
        self.tabelas = {'usuarios', 'funcionarios', 'livros', 'emprestimos'}
        
        # Sempre usar armazenamento em arquivo
        self.storage = FileStorage.FileStorage(filename)
        self.db = DB(self.storage)
        self.connection = self.db.open()
        self.root = self.connection.root()
        
        # Inicializa as "tabelas"
        for tabela in self.tabelas:
            if not hasattr(self.root, tabela):
                setattr(self.root, tabela, OOBTree())
        transaction.commit()

    @contextmanager
    def transaction_manager(self):
        try:
            yield
            transaction.commit()
        except:
            transaction.abort()
            raise

    def fechar(self):
        """Fecha todas as conexões com o banco de dados"""
        for conn in [self.connection, self.db, self.storage]:
            if conn is not None:
                conn.close()

    # Cache para buscas frequentes
    _cache_usuarios_por_cpf = {}
    _cache_funcionarios_por_matricula = {}
    
    def salvar_usuario(self, usuario):
        with self.transaction_manager():
            self.root.usuarios[usuario.id] = usuario
            self._cache_usuarios_por_cpf[usuario.cpf] = usuario

    def buscar_usuario_por_cpf(self, cpf: str) -> Optional['Usuario']:
        # Primeiro tenta no cache
        if cpf in self._cache_usuarios_por_cpf:
            return self._cache_usuarios_por_cpf[cpf]
        
        # Se não encontrar, busca no banco e atualiza o cache
        for usuario in self.root.usuarios.values():
            if usuario.cpf == cpf:
                self._cache_usuarios_por_cpf[cpf] = usuario
                return usuario
        return None

    def salvar_funcionario(self, funcionario):
        with self.transaction_manager():
            self.root.funcionarios[funcionario.id] = funcionario
            self._cache_funcionarios_por_matricula[funcionario.matricula] = funcionario

    def buscar_funcionario_por_matricula(self, matricula: str) -> Optional['Funcionario']:
        # Primeiro tenta no cache
        if matricula in self._cache_funcionarios_por_matricula:
            return self._cache_funcionarios_por_matricula[matricula]
        
        # Se não encontrar, busca no banco e atualiza o cache
        for funcionario in self.root.funcionarios.values():
            if funcionario.matricula == matricula:
                self._cache_funcionarios_por_matricula[matricula] = funcionario
                return funcionario
        return None

    def salvar_livro(self, livro):
        with self.transaction_manager():
            self.root.livros[livro.id] = livro

    def buscar_livro(self, id: int) -> Optional['Livro']:
        return self.root.livros.get(id)

    def listar_livros(self) -> List['Livro']:
        return list(self.root.livros.values())

    def listar_livros_disponiveis(self) -> List['Livro']:
        return [livro for livro in self.root.livros.values() if livro.disponivel]

    def salvar_emprestimo(self, emprestimo):
        with self.transaction_manager():
            self.root.emprestimos[emprestimo.id] = emprestimo

    def buscar_emprestimo(self, id: int) -> Optional['Emprestimo']:
        return self.root.emprestimos.get(id)

    def listar_emprestimos(self) -> List['Emprestimo']:
        return list(self.root.emprestimos.values())

    def listar_emprestimos_ativos(self) -> List['Emprestimo']:
        return [emp for emp in self.root.emprestimos.values() if not emp.devolvido]

    def listar_emprestimos_usuario(self, usuario_id: int) -> List['Emprestimo']:
        return [emp for emp in self.root.emprestimos.values() 
                if emp.usuario.id == usuario_id and not emp.devolvido]

    def salvar_objeto(self, obj: Any, tabela: str) -> None:
        """Método genérico para salvar objetos"""
        try:
            getattr(self.root, tabela)[obj.id] = obj
            transaction.commit()
            self.clear_caches()
            logger.info(f"Objeto salvo com sucesso na tabela {tabela}")
        except Exception as e:
            logger.error(f"Erro ao salvar objeto: {e}")
            transaction.abort()
            raise

    def buscar_objeto(self, id: int, tabela: str) -> Optional[Any]:
        try:
            return getattr(self.root, tabela).get(id)
        except Exception as e:
            logger.error(f"Erro ao buscar objeto: {e}")
            return None

    def listar_objetos(self, tabela: str) -> List[Any]:
        try:
            return list(getattr(self.root, tabela).values())
        except Exception as e:
            logger.error(f"Erro ao listar objetos: {e}")
            return []

    @lru_cache(maxsize=1000)
    def buscar_usuario_por_cpf(self, cpf: str) -> Optional['Usuario']:
        try:
            for usuario in self.root.usuarios.values():
                if usuario.cpf == cpf:
                    return usuario
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por CPF: {e}")
            return None

    @lru_cache(maxsize=1000)
    def buscar_funcionario_por_matricula(self, matricula: str) -> Optional['Funcionario']:
        try:
            for func in self.root.funcionarios.values():
                if func.matricula == matricula:
                    return func
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar funcionário por matrícula: {e}")
            return None

    def clear_caches(self) -> None:
        self.buscar_usuario_por_cpf.cache_clear()
        self.buscar_funcionario_por_matricula.cache_clear()

    def listar_funcionarios(self):
        """Retorna lista de todos os funcionários"""
        return list(self.root.funcionarios.values())

    def listar_usuarios(self):
        """Retorna lista de todos os usuários"""
        return list(self.root.usuarios.values())