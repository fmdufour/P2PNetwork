#/* --------------------------------------------------------------------------------------
#   Entrada da exeucao do trabalho
#   Objetivo: Tem como objetivo a entrada de parametros de execucao e a criacao
#             do objeto da classe PeerNode para iniciar a rede p2p
#
#  Autor: Fernando M Dufour e Carolina Lara Moraes
#   Disciplina: Redes II
#   Data da ultima atualizacao: 2017/1
#----------------------------------------------------------------------------------------*/

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

    #Realiza validacao dos parametros fornecidos
    #id vai ser o identificador do peer
    #numberOfPeers eh usado para definir o tamanho da rede p2p1
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

    #carrega o id, ip e porta dos peers da rede com base no arquivo json
    with open('peers.json') as file:
        peer_info = json.load(file)

    #intancia a classe para realizar o log de execucao
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

    #cria o nodo da rede p2p
    peer = PeerNode(peer_info, id, logger, numberOfPeers)

    #inicia a rede p2p
    peer.start_network()

    time.sleep(1000000000)


if __name__ == "__main__":
    main()
