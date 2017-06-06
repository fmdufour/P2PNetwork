class Peer:
    #socket usado para enviar mensagens ao peer
    sock_to_send = None
    #socket usado para receber mensagens do peer
    sock_to_receive = None
    #flag usada para marcar se o peer esta disconectado da rede
    disconnected = False
    #flag para saber se o peer eh o lider da rede ou nao
    leader = False

    def __init__(self, id, ip, port):
        self.id = id
        self.ip = ip
        self.port = port
