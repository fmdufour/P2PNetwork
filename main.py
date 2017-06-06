import sys
import json
from peerNode import *
from logger import Logger
import time

def main():
    if(len(sys.argv) != 2):
        print("A execucao deve ser realizada da seguinte maneira:")
        print("python Main.py <Id Peer>")
        sys.exit(1)

    id = sys.argv[1]

    try:
        id = int(id)
        if id < 0 or id > 3:
            sys.exit("O parametro <Id Peer> deve ser um inteiro de 0 a 3")
    except :
        sys.exit("O parametro <Id Peer> deve ser um inteiro de 0 a 3")

    with open('peers.json') as file:
        peer_info = json.load(file)

    logger = Logger()

    logger.log("========================================================")
    logger.log("   Inicio da execucao do programa que implementa a      ")
    logger.log("          eleicao de lideres entre Peers TCP            ")
    logger.log("========================================================")
    logger.log(" Prof. Elias P. Duarte Jr.  -  Redes de Computadores II ")
    logger.log("        Fernando M Dufour - Carolina de Lara Moraes     ")
    logger.log("========================================================")
    logger.log("=================  PEER "+ str(id) + "  =============================")
    logger.log("========================================================")

    peer = PeerNode(peer_info, id, logger)

    peer.start_network()

    time.sleep(1000000000)


if __name__ == "__main__":
    main()
