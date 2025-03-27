import sys
print("Python sendo usado:", sys.executable)
print("Versão do Python:", sys.version)
print("-------------------")

from modelos import Usuario, Funcionario, Livro, Emprestimo
from biblioteca_db import BibliotecaDB
import os
import tempfile

# Inicialização do banco de dados com caminho fixo
db_path = 'biblioteca.fs'

db = BibliotecaDB(db_path)

def cadastrar_usuario():
    print("\n=== Cadastro de Usuário ===")

    nome = input("Nome: ")
    cpf = input("CPF: ")
    email = input("Email: ")
    numero_cartao = input("Número do Cartão: ")
    
    id_usuario = len(db.listar_usuarios()) + 1
    usuario = Usuario(id_usuario, nome, cpf, email, numero_cartao)
    db.salvar_usuario(usuario)
    
    print("\nUsuário cadastrado com sucesso!")
    return usuario

def cadastrar_funcionario(first):
    print("\n=== Cadastro de Funcionário ===")
    resposta = ""
    if first == False:
        resposta = input("Quer proceder novamente?")

    if resposta == "n":
        return
    
    nome = input("Nome: ")
    cpf = input("CPF: ")
    email = input("Email: ")
    matricula = input("Matrícula: ")
    cargo = input("Cargo: ")
    
    id_funcionario = len(db.root.funcionarios) + 1
    try:
        funcionario = Funcionario(id_funcionario, nome, cpf, email, matricula, cargo)
        db.salvar_funcionario(funcionario)
    
        print("\nFuncionário cadastrado com sucesso!")
        return funcionario
    except ValueError:
        print("Dados inválidos. Try again")
        first = False
        cadastrar_funcionario(first)

def cadastrar_livro():
    print("\n=== Cadastro de Livro ===")
    titulo = input("Título: ")
    autor = input("Autor: ")
    isbn = input("ISBN: ")
    
    id_livro = len(db.listar_livros()) + 1
    livro = Livro(id_livro, titulo, autor, isbn)
    db.salvar_livro(livro)
    
    print("\nLivro cadastrado com sucesso!")
    return livro

def realizar_emprestimo(usuario):
    print("\n=== Realizar Empréstimo ===")
    print("\nLivros disponíveis:")
    livros_disponiveis = db.listar_livros_disponiveis()
    
    if not livros_disponiveis:
        print("Não há livros disponíveis no momento.")
        return
    
    for livro in livros_disponiveis:
        print(f"ID: {livro.id} - Título: {livro.titulo} - Autor: {livro.autor}")
    
    try:
        id_livro = int(input("\nDigite o ID do livro desejado: "))
        livro = db.buscar_livro(id_livro)
        
        if not livro:
            print("Livro não encontrado!")
            return
        
        if not livro.disponivel:
            print("Livro não está disponível!")
            return
        
        id_emprestimo = len(db.listar_emprestimos()) + 1
        emprestimo = Emprestimo(id_emprestimo, usuario, livro)
        db.salvar_emprestimo(emprestimo)
        
        print("\nEmpréstimo realizado com sucesso!")
        print(f"Data de devolução: {emprestimo.data_devolucao.strftime('%d/%m/%Y')}")
        
    except ValueError:
        print("ID inválido!")

def main():
    try:
        while True:
            print("\n=== Sistema de Biblioteca ===")
            print("1 - Acesso de Usuário")
            print("2 - Acesso de Funcionário")
            print("3 - Sair")
            
            opcao_inicial = input("\nEscolha uma opção: ")
            
            if opcao_inicial == "1":
                # Menu de usuário
                print("\n=== Acesso de Usuário ===")
                print("1 - Novo cadastro")
                print("2 - Já sou cadastrado")
                opcao_usuario = input("\nEscolha uma opção: ")
                
                if opcao_usuario == "1":
                    usuario = cadastrar_usuario()
                elif opcao_usuario == "2":
                    # Buscar usuário existente
                    cpf = input("\nDigite seu CPF: ")
                    usuario = db.buscar_usuario_por_cpf(cpf)
                    if not usuario:
                        print("Usuário não encontrado!")
                        continue
                else:
                    print("Opção inválida!")
                    continue
                
                # Menu de operações do usuário
                while True:
                    print("\n=== Menu do Usuário ===")
                    print("1 - Realizar empréstimo")
                    print("2 - Listar livros disponíveis")
                    print("3 - Meus empréstimos ativos")
                    print("4 - Voltar ao menu principal")
                    
                    opcao = input("\nEscolha uma opção: ")
                    
                    if opcao == "1":
                        realizar_emprestimo(usuario)
                    elif opcao == "2":
                        print("\n=== Livros Disponíveis ===")
                        livros_disponiveis = db.listar_livros_disponiveis()
                        for livro in livros_disponiveis:
                            print(f"ID: {livro.id} - Título: {livro.titulo} - Autor: {livro.autor}")
                    elif opcao == "3":
                        print("\n=== Seus Empréstimos Ativos ===")
                        emprestimos_ativos = db.listar_emprestimos_usuario(usuario.id)
                        for emp in emprestimos_ativos:
                            print(f"Livro: {emp.livro.titulo}")
                            print(f"Data de devolução: {emp.data_devolucao.strftime('%d/%m/%Y')}")
                            print("---")
                    elif opcao == "4":
                        break
                    else:
                        print("Opção inválida!")
                        
            elif opcao_inicial == "2":
                # Menu de funcionário
                print("\n=== Acesso de Funcionário ===")
                print("1 - Novo cadastro")
                print("2 - Já sou cadastrado")
                opcao_funcionario = input("\nEscolha uma opção: ")
                
                if opcao_funcionario == "1":
                    funcionario = cadastrar_funcionario(True)
                elif opcao_funcionario == "2":
                    # Buscar funcionário existente
                    matricula = input("\nDigite sua matrícula: ")
                    funcionario = db.buscar_funcionario_por_matricula(matricula)
                    if not funcionario:
                        print("Funcionário não encontrado!")
                        continue
                else:
                    print("Opção inválida!")
                    continue
                
                # Menu de operações do funcionário
                while True:
                    print("\n=== Menu do Funcionário ===")
                    print("1 - Cadastrar novo livro")
                    print("2 - Listar todos os livros")
                    print("3 - Listar todos os empréstimos")
                    print("4 - Cadastrar novo usuário")
                    print("5 - Voltar ao menu principal")
                    
                    opcao = input("\nEscolha uma opção: ")
                    
                    if opcao == "1":
                        cadastrar_livro()
                    elif opcao == "2":
                        print("\n=== Todos os Livros ===")
                        todos_livros = db.listar_livros()
                        for livro in todos_livros:
                            status = "Disponível" if livro.disponivel else "Emprestado"
                            print(f"ID: {livro.id} - Título: {livro.titulo} - Autor: {livro.autor} - Status: {status}")
                    elif opcao == "3":
                        print("\n=== Todos os Empréstimos ===")
                        emprestimos_ativos = db.listar_emprestimos_ativos()
                        for emp in emprestimos_ativos:
                            print(f"Usuário: {emp.usuario.nome}")
                            print(f"Livro: {emp.livro.titulo}")
                            print(f"Data de devolução: {emp.data_devolucao.strftime('%d/%m/%Y')}")
                            print("---")
                    elif opcao == "4":
                        cadastrar_usuario()
                    elif opcao == "5":
                        break
                    else:
                        print("Opção inválida!")
            
            elif opcao_inicial == "3":
                print("\nSaindo do sistema...")
                break
            else:
                print("\nOpção inválida!")

    finally:
        # Fecha a conexão com o banco
        db.fechar()

if __name__ == "__main__":
    main()