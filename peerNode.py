#/* --------------------------------------------------------------------------------------
#   Classe PeerNode
#   Objetivo: A classe representa um Nodo em uma rede PeerToPeer
#             Tem como objetivo a conexao com os outros peers da rede, o envio de heartbeats
#             E a eleicao de lideres na rede, conforme a especificacao do trabalho indica
#
#  Autor: Fernando M Dufour e Carolina Lara Moraes
#   Disciplina: Redes II
#   Data da ultima atualizacao: 2017/1
#----------------------------------------------------------------------------------------*/
from socket import *
from peer import Peer
import threading
import time

HEARTBEAT = "<3"
LEADER_CHANGE = "!!!"

class PeerNode:
    server_sock = None
    peers = None
    connected_clients = False
    connected_server = False
    numberOfPeers =  0

    #construtor da classe PeerNode
    def __init__(self, properties, node_id, logger, numberOfPeers):
        #seta o numero maximo de peers da rede,
        #inicia o vetor de peers e seta atributos da classe
        self.numberOfPeers = numberOfPeers
        self.logger = logger
        self.peers = [None] * numberOfPeers
        self.id = properties[node_id]["id"]
        self.ip = properties[node_id]["ip"]
        self.port = properties[node_id]["port"]

        self.logger.log("Iniciando o Peer de:")
        self.logger.log("   Id    -> " + str(self.id))
        self.logger.log("   IP    -> " + str(self.ip))
        self.logger.log("   Porta -> " + str(self.port))


        self.server_sock = socket(AF_INET, SOCK_STREAM)
        self.server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        #inicia o vetor de peers com as informacoes dos peers da rede
        self.init_peers(properties)
        #faz o bind do socket no ip e porta do host e coloca no modo de escuta
        self.server_sock.bind((self.ip, self.port))
        self.server_sock.listen(8)

        self.logger.log("Peer " + str(self.id) + " (eu) esta no modo escuta na porta " + str(self.port))
        self.logger.log("Iniciando thread para esperar conexoes dos clientes")
        #inicia thread que vai esperar a conexao dos outros peers da rede
        t = threading.Thread(target=self.wait_for_connections)
        t.daemon = True
        t.start()
        #inicia a thread que ira tentar a conexao com os outros peers da rede
        self.logger.log("Iniciando thread para tentar a conexao com os outros Peers")
        t = threading.Thread(target=self.try_connect)
        t.daemon = True
        t.start()

        #espera todos os peers se conectarem e tambem a conexao com os outros
        while(not(self.connected_clients and self.connected_server)):
            pass

        self.logger.log("## O peer conseguiu se conectar e recebeu conexao dos demais peers!")
        self.logger.log("## Rede Peer to Peer conectada!")


    def start_network(self):
        self.logger.log("Iniciando Threads para envio e escuta de Heartbeats")
        #para cada peer da rede que nao seja o peer da maquina que esta executando o programa:
        #inicia uma thread para receber mensagens e para emitir heartbeats aos outros Peers
        for peer in self.peers:
            if (peer.id == self.id):
                continue
            t = threading.Thread(target=self.listen_messages, args=(peer,))
            t.daemon = True
            t.start()
            t = threading.Thread(target=self.start_heartbeats, args=(peer,))
            t.daemon = True
            t.start()

        #Aguarda um segundo para esperar os heartbeats terem sido enviados, mas poderia ser um while com alguma flag
        time.sleep(1)
        self.logger.log("Recebi Heartbeat de todos os outros Peers, agora iremos eleger um Lider")
        #elege o lider da rede
        self.ellect_new_leader()
        #inicia uma thread para exibir na tela e log o lider atual a cada 2 segundos
        t = threading.Thread(target=self.display_leader)
        t.daemon = True
        t.start()


    #metodo executado em thread com a funcao de exibir o lider da rede
    def display_leader(self):
        while(1):
            for peer in self.peers:
                if(peer.leader):
                    self.logger.log("O lider atual eh o Peer " + str(peer.id))
                    break
            time.sleep(2)


    #metodo executado em thread para receber mensagens do peer passado por parametro
    def listen_messages(self, peer):
        while True:
            msg = peer.sock_to_receive.recv(1028)
            if not msg:
                peer.disconnected = True
                self.logger.log("O Peer " + str(peer.id) + " desconectou-se")
                if(peer.leader):
                    peer.leader = False
                    self.logger.log("Enviando mensagem URGENTE TCP - Lider mudou!")
                    self.send_to_all(LEADER_CHANGE)
                    self.ellect_new_leader()
                break
            if(msg == HEARTBEAT):
                self.logger.log("Recebi Heartbeat do Peer " + str(peer.id) + ", entao ele continua conectado!")
                peer.alive = True
            elif(msg == LEADER_CHANGE):
                self.logger.log("!! Mensagem TCP URGENTE recebida (Lider desconectou-se)")
                self.ellect_new_leader()

    #metodo para eleicao de um lider na rede p2p
    def ellect_new_leader(self):
        self.logger.log("Iniciando nova eleicao de lider")
        for peer in self.peers:
            if(peer.id == self.id or (not peer.disconnected)):
                self.logger.log("$$ O Peer " + str(peer.id) + " foi eleito o novo lider!")
                peer.leader = True
                break

    #metodo executado em thread para o envio de heatbeats a cada 2 segundos para o peer passado por parametro
    def start_heartbeats(self, peer):
        while True:
            try:
                if(not peer.disconnected):
                    self.logger.log("Peer " + str(self.id) + " (eu) enviando Heartbeat para Peer " + self.peer_info(peer))
                    peer.sock_to_send.send(HEARTBEAT)
            except e:
                pass
            time.sleep(2)

    #metodo para broadcast aos peers da rede
    def send_to_all(self, message):
        for peer in self.peers:
            if(peer.id == self.id):
                continue
            if(not peer.disconnected and peer.alive):
                peer.sock_to_send.send(message)

    #metodo para tentar a conexao com todos os peers da rede
    def try_connect(self):
        for peer in self.peers:
            if (peer.id == self.id):
                continue
            #cria um novo socket
            sock = socket(AF_INET, SOCK_STREAM)
            while True:
                try:
                    #vai tentando conectar ao peer
                    sock.connect((peer.ip, peer.port))
                    sock.send(str(self.id))
                    self.logger.log("Consegui conectar meu cliente com sucesso ao Peer " + self.peer_info(peer))
                    break
                except Exception as e:
                    continue
            peer.sock_to_send = sock

        #seta como true a flag que esta segurando a thread principal
        self.connected_clients = True


    #metodo para aguardar a conexao dos peers da rede
    def wait_for_connections(self):
        connected_peers = 0
        self.logger.log("Aguardando requisicoes de conexoes...")
        while connected_peers < self.numberOfPeers-1:
            sock, addr = self.server_sock.accept()
            #recebe o id do peer que acabou de se conectar
            id_connected = int(sock.recv(1028))
            self.logger.log("Conexao recebida do Peer de Id=" + str(id_connected) + ", Ip=" +addr[0])
            self.peers[id_connected].sock_to_receive = sock
            connected_peers += 1
        #seta como true a flag que esta segurando a thread principal
        self.connected_server = True

    #metodo para inicializar o vetor de peers com base no arquivo .json com as infos
    def init_peers(self, properties):
        i = 1
        for p in properties:
            if i <= self.numberOfPeers:
                self.peers[p["id"]] = Peer(p["id"], p["ip"], p["port"])
                i+=1

    #metodo auxiliar para ser usado na funcao de log
    def peer_info(self, peer):
        return " (Id=" + str(peer.id) + ", Ip=" + peer.ip + ", Porta="+ str(peer.port) + ")"
