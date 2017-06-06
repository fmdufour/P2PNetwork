import sys
import json
from peerNode import *
from logger import Logger
import time

def main():
    if(len(sys.argv) != 3):
        print("A execucao deve ser realizada da seguinte maneira:")
        print("python Main.py <Id Peer> <Numero de Peers da Rede>")
        sys.exit(1)

    id = sys.argv[1]
    numberOfPeers = sys.argv[2]

    try:
        id = int(id)
        if id < 0 or id > numberOfPeers:
            sys.exit("O parametro <Id Peer> deve ser um inteiro de 0 a N-1 (Numero de Peers da Rede)")
    except :
        sys.exit("O parametro <Id Peer> deve ser um inteiro de 0 a N-1 (N = Numero de Peers da Rede)")

    try:
        numberOfPeers = int(numberOfPeers)
        if numberOfPeers < 3 or numberOfPeers > 4:
            sys.exit("O parametro <Numero de Peers da Rede> deve ser um inteiro de 3 a 4")
    except :
        sys.exit("O parametro <Numero de Peers da Rede> deve ser um inteiro de 3 a 4")

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
    logger.log("Foi informado que o tamanho da rede sera de " + str(numberOfPeers) + " Peers")

    peer = PeerNode(peer_info, id, logger, numberOfPeers)

    peer.start_network()

    time.sleep(1000000000)


if __name__ == "__main__":
    main()
