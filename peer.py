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
