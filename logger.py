import time

class Logger:
    file = None
    def __init__(self):
            self.file = open("./log/log_" + str(time.time())[:-3] + ".txt", "w")

    def log(self, msg):
        self.file.write(msg + "\n")
        print(msg)
