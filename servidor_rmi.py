import socket
import threading
import time

HOST = "0.0.0.0"
PORTA = 5000

class Biblioteca:
    def __init__(self):
        # Acervo em memória
        self.acervo = {
            "123-4": {"titulo": "Sistemas Distribuídos", "total": 1, "disponivel": 1}
        }
        # Mutex para garantir que as threads de conexão não sobrescrevam o acervo simultaneamente
        self.lock = threading.Lock()

    def emprestar_livro(self, isbn, matricula):
        with self.lock:
            livro = self.acervo.get(isbn)
            if not livro:
                return "ERRO: Livro não encontrado."

            if livro["disponivel"] > 0:
                time.sleep(0.5) # Simula latência de rede/I-O para forçar o teste de concorrência
                livro["disponivel"] -= 1
                return f"SUCESSO: '{livro['titulo']}' emprestado para {matricula}."
            else:
                return "FALHA: Livro esgotado no momento."

    def consultar_disponibilidade(self, isbn):
        livro = self.acervo.get(isbn)
        return str(livro["disponivel"] > 0) if livro else "False"

# Instância global da biblioteca para ser acedida pelas threads
biblioteca = Biblioteca()

def atender_cliente(cliente, endereco):
    print(f"[+] Cliente conectado: {endereco}")
    try:
        while True:
            dados = cliente.recv(1024)
            if not dados:
                break
                
            mensagem = dados.decode("utf-8").split("|")
            metodo = mensagem[0]

            if metodo == "emprestar_livro":
                resposta = biblioteca.emprestar_livro(mensagem[1], mensagem[2])
            elif metodo == "consultar_disponibilidade":
                resposta = biblioteca.consultar_disponibilidade(mensagem[1])
            else:
                resposta = "ERRO: Método desconhecido."

            cliente.send(resposta.encode("utf-8"))
            
    except Exception as erro:
        print(f"Erro com o cliente {endereco}: {erro}")
    finally:
        cliente.close()
        print(f"[-] Cliente desconectado: {endereco}")

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORTA))
    servidor.listen()

    print("=" * 50)
    print("SERVIDOR DE BIBLIOTECA (RMI via Sockets)")
    print("=" * 50)
    print(f"Servidor aguardando conexões na porta {PORTA}...")

    while True:
        cliente, endereco = servidor.accept()
        thread = threading.Thread(target=atender_cliente, args=(cliente, endereco))
        thread.start()

if __name__ == "__main__":
    iniciar_servidor()