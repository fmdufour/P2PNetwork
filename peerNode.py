from socket import *
from peer import Peer
import threading
import time

HEARTBEAT = "<3"
LEADER_CHANGE = "!!!"

class PeerNode:
    server_sock = None
    peers = [None] * 4
    connected_clients = False
    connected_server = False

    def __init__(self, properties, node_id, logger):
        self.logger = logger
        self.id = properties[node_id]["id"]
        self.ip = properties[node_id]["ip"]
        self.port = properties[node_id]["port"]

        self.logger.log("Iniciando o Peer de:")
        self.logger.log("   Id    -> " + str(self.id))
        self.logger.log("   IP    -> " + str(self.ip))
        self.logger.log("   Porta -> " + str(self.port))

        self.server_sock = socket(AF_INET, SOCK_STREAM)
        self.server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.init_peers(properties)
        self.server_sock.bind((self.ip, self.port))
        self.server_sock.listen(8)

        self.logger.log("Peer esta no modo escuta na porta " + str(self.port))

        self.logger.log("Iniciando thread para esperar conexoes dos clientes")
        t = threading.Thread(target=self.wait_for_connections)
        t.daemon = True
        t.start()

        #self.logger.log("Iniciando thread para tentar a conexao com os outros Peers")
        t = threading.Thread(target=self.try_connect)
        t.daemon = True
        t.start()

        while(not(self.connected_clients and self.connected_server)):
            pass

        self.logger.log("## O peer conseguiu se conectar e recebeu conexao dos demais peers!")
        self.logger.log("## Rede Peer to Peer conectada!")


    def start_network(self):
        self.logger.log("Iniciando Threads para envio e escuta de Heartbeats")
        for peer in self.peers:
            if (peer.id == self.id):
                continue
            t = threading.Thread(target=self.listen_messages, args=(peer,))
            t.daemon = True
            t.start()
            t = threading.Thread(target=self.start_heartbeats, args=(peer,))
            t.daemon = True
            t.start()

        time.sleep(1)
        self.ellect_new_leader()

        t = threading.Thread(target=self.display_leader)
        t.daemon = True
        t.start()


    def display_leader(self):
        while(1):
            for peer in self.peers:
                if(peer.leader):
                    self.logger.log("O lider atual eh o peer de Id " + str(peer.id))
                    break
            time.sleep(2)


    def listen_messages(self, peer):
        while True:
            msg = peer.sock_to_receive.recv(1028)
            if not msg:
                peer.disconnected = True
                self.logger.log("Peer de Id=" + str(peer.id) + " desconectou-se")
                if(peer.leader):
                    peer.leader = False
                    self.logger.log("Enviando mensagem URGENTE TCP - Lider mudou!")
                    self.send_to_all(LEADER_CHANGE)
                    self.ellect_new_leader()
                break
            if(msg == HEARTBEAT):
                self.logger.log("<3 Heartbeat recebido do Peer de Id=" + str(peer.id))                
                peer.alive = True
            elif(msg == LEADER_CHANGE):
                self.logger.log("!! Mensagem TCP URGENTE recebida (Lider desconectou-se)")
                self.ellect_new_leader()


    def ellect_new_leader(self):
        self.logger.log("Iniciando nova eleicao de lider")
        for peer in self.peers:
            if(peer.id == self.id or (not peer.disconnected)):
                self.logger.log("$$ O peer de Id " + str(peer.id) + " foi eleito o novo lider!")
                peer.leader = True
                break

    def start_heartbeats(self, peer):
        while True:
            try:
                if(not peer.disconnected):
                    self.logger.log("Enviando Heartbeat para peer:" + peer_info(peer))
                    peer.sock_to_send.send(HEARTBEAT)
            except:
                pass
            time.sleep(2)


    def send_to_all(self, message):
        for peer in self.peers:
            if(peer.id == self.id):
                continue
            if(not peer.disconnected and peer.alive):
                peer.sock_to_send.send(message)

    def try_connect(self):
        for peer in self.peers:
            if (peer.id == self.id):
                continue

            sock = socket(AF_INET, SOCK_STREAM)
            while True:
                try:
                    sock.connect((peer.ip, peer.port))
                    sock.send(str(self.id))
                    self.logger.log("Conectado com sucesso ao Peer " + self.peer_info(peer))
                    break
                except Exception as e:
                    continue
            peer.sock_to_send = sock

        self.connected_clients = True


    def wait_for_connections(self):
        connected_peers = 0
        while connected_peers < 3:
            sock, addr = self.server_sock.accept()
            id_connected = int(sock.recv(1028))
            self.logger.log("Conexao recebida do Peer de Id=" + str(id_connected) + ", Ip=" +addr[0])
            self.peers[id_connected].sock_to_receive = sock
            connected_peers += 1
        self.connected_server = True


    def init_peers(self, properties):
        for p in properties:
            self.peers[p["id"]] = Peer(p["id"], p["ip"], p["port"])

    def peer_info(self, peer):
        return " (Id=" + str(peer.id) + ", Ip=" + peer.ip + ", Porta="+ str(peer.port) + ")"
