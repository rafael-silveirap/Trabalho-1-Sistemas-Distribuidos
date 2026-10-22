import socket
import threading

HOST = "127.0.0.1"
PORTA = 5000

class ProxyBiblioteca:
    """Classe que mascara a comunicação de rede, fazendo-a parecer chamadas de função locais"""
    def __init__(self, host, porta):
        self.host = host
        self.porta = porta

    def _chamar_remoto(self, mensagem):
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.connect((self.host, self.porta))
        cliente.send(mensagem.encode("utf-8"))
        resposta = cliente.recv(1024).decode("utf-8")
        cliente.close()
        return resposta

    def emprestar_livro(self, isbn, matricula):
        return self._chamar_remoto(f"emprestar_livro|{isbn}|{matricula}")

    def consultar_disponibilidade(self, isbn):
        return self._chamar_remoto(f"consultar_disponibilidade|{isbn}")


def acao_concorrente_cliente(matricula, isbn):
    proxy = ProxyBiblioteca(HOST, PORTA)
    print(f"[{matricula}] Tentando emprestar o livro {isbn}...")
    resposta = proxy.emprestar_livro(isbn, matricula)
    print(f"[{matricula}] Resposta do Servidor: {resposta}")

def iniciar_cliente():
    isbn_alvo = "123-4"
    proxy = ProxyBiblioteca(HOST, PORTA)
    
    print("=" * 40)
    print("TESTE DE CONCORRÊNCIA")
    print("=" * 40)
    print(f"Disponibilidade inicial (ISBN {isbn_alvo}): {proxy.consultar_disponibilidade(isbn_alvo)}")
    print("-" * 40)

    # Dispara múltiplas threads simultâneas para causar uma condição de corrida no servidor
    threads = []
    for i in range(5):
        t = threading.Thread(
            target=acao_concorrente_cliente, 
            args=(f"ALUNO_00{i+1}", isbn_alvo)
        )
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print("-" * 40)
    print(f"Disponibilidade final (ISBN {isbn_alvo}): {proxy.consultar_disponibilidade(isbn_alvo)}")

if __name__ == "__main__":
    iniciar_cliente()