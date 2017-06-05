from socket import *
import threading
import time

HEARTBEAT = "<3"
LEADER_CHANGE = "!!!"

class Peer:
    connection = None
    sock_to_send = None
    sock_to_receive = None
    alive = True
    disconnected = False
    leader = False

    def __init__(self, id, ip, port):
        self.id = id
        self.ip = ip
        self.port = port

class PeerNode:
    server_sock = None
    peers = [None] * 4
    connected_clients = False
    connected_server = False

    def __init__(self, properties, node_id):
        self.id = properties[node_id]["id"]
        self.ip = properties[node_id]["ip"]
        self.port = properties[node_id]["port"]
        self.server_sock = socket(AF_INET, SOCK_STREAM)
        self.server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.init_peers(properties)
        print("Escutando no endereco " + self.ip + ":" + str(self.port))
        self.server_sock.bind((self.ip, self.port))
        self.server_sock.listen(4)

        t = threading.Thread(target=self.wait_for_connections)
        t.daemon = True
        t.start()

        t = threading.Thread(target=self.try_connect)
        t.daemon = True
        t.start()

        while(not(self.connected_clients and self.connected_server)):
            pass

        print("## Rede Peer to Peer conectada ##")

    def start_network(self):
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
                    print("O lider atual eh o " + str(peer.id))
                    break
            time.sleep(2)


    def listen_messages(self, peer):
        while True:
            msg = peer.sock_to_receive.recv(3)
            if not msg:
                peer.disconnected = True
                print("Peer " + str(peer.id) + " se desconectou")
                if(peer.leader):
                    peer.leader = False
                    self.send_to_all(LEADER_CHANGE)
                    self.ellect_new_leader()
                break
            print("Mensagem recebida do peer " + str(peer.id) + ": " + msg)
            if(msg == HEARTBEAT):
                peer.alive = True
            elif(msg == LEADER_CHANGE):
                self.ellect_new_leader()


    def ellect_new_leader(self):
        for peer in self.peers:
            if(peer.id == self.id or (not peer.disconnected)):
                peer.leader = True
                break

    def start_heartbeats(self, peer):
        while True:
            try:
                if(not peer.disconnected):
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

            print("Tentando conectar a " + peer.ip + ":" + str(peer.port))

            sock = socket(AF_INET, SOCK_STREAM)
            while True:
                try:
                    sock.connect((peer.ip, peer.port))
                    sock.send(str(self.id))
                    break
                except Exception as e:
                    continue
            print("conectado ao peer " + peer.ip + ":" + str(peer.port))
            peer.sock_to_send = sock

        self.connected_clients = True


    def wait_for_connections(self):
        connected_peers = 0
        print("Aguardando conexoes...")

        while connected_peers < 3:
            sock, addr = self.server_sock.accept()
            print("Recebeu conexao de " + str(addr))
            id_connected = int(sock.recv(1))
            self.peers[id_connected].sock_to_receive = sock
            connected_peers += 1
        self.connected_server = True


    def init_peers(self, properties):
        for p in properties:
            self.peers[p["id"]] = Peer(p["id"], p["ip"], p["port"])
