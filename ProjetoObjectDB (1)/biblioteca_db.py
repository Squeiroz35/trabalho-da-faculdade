from typing import List

class BibliotecaDB:
    def listar_funcionarios(self) -> List['Funcionario']:
        """Retorna lista de todos os funcionários"""
        return list(self.root.funcionarios.values())

    def listar_usuarios(self) -> List['Usuario']:
        """Retorna lista de todos os usuários"""
        return list(self.root.usuarios.values()) 