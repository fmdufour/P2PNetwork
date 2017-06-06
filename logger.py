#/* --------------------------------------------------------------------------------------
#   Classe Logger
#   Objetivo: Abstrair a criacao log de mensagens em arquivo
#
#  Autor: Fernando M Dufour e Carolina Lara Moraes
#   Disciplina: Redes II
#   Data da ultima atualizacao: 2017/1
#----------------------------------------------------------------------------------------*/
import time

#classe com o objetivo de abstrair o log de mensagens
class Logger:
    file = None
    def __init__(self):
            #cria um arquivo de log na pasta /log com um timestamp
            self.file = open("./log/log_" + str(time.time())[:-3] + ".txt", "w")

    def log(self, msg):
        self.file.write(msg + "\n")
        print(msg)
