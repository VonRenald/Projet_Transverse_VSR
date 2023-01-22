import os
import sys
import time
import socketserver
import threading

import socket

import docker
import subprocess

from multiprocessing import Semaphore
from multiprocessing import Process

# +-----------------------------------------+
# |     Declaration des variables global    |
# +-----------------------------------------+

sem = None
serverC = None
serverW = None

count = 0 # --------nombre de packet traité

portC = 0 # --------port d'entrée des client
nexPort = 0 # ------porchain port a utiliser pour le docker
portSleep = 0 # ----port du docker en veille
portInUse = [] # ---liste des ports actuellement utilisé

nbDock = 1
next_max = 3 # -----valeur du ping a atteindre pour la création du prochain docker

clientD = None # ---cration du docker

delta_Moy = [0] # --liste des dernier ping pour créer une moyenne

atom = False # -----zone atomique

# +-----------------------------------------+
# |         Declaration des fonctions       |
# +-----------------------------------------+

def send_msg(msg, port, wait_answer = True):
    # +-----------------------------------------+
    # |         envoie un  message au port      |
    # |         demandé, attent la reponse      |
    # |         et  retourne  la taille du      |
    # |             msg lus et le ping          |
    # +-----------------------------------------+
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:

        client.connect(('127.0.0.1',port))
        t1 = time.time()
        client.send(msg)
        if wait_answer:
            response = client.recv(1024)
            t2 = time.time()
            print("return in ",t2-t1,"\t- ",response,end=' ')
            delta = t2-t1 
            return response, delta
    return None, 0



def read_int(filename, default):
    try:
        with open(filename, 'r') as file:
            return int(f.read())
    except:
        return default

def sem_init():
    global sem
    ## 1 worker per 100MB
    unit = 100*1000*1000
    nb_parallel = read_int('/sys/fs/cgroup/memory.max', 3*unit) // unit
    sem = Semaphore(value = nb_parallel)


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    # +-----------------------------------------+
    # |     fonction appelé a chaque msg        |
    # +-----------------------------------------+
    def handle(self):
        global count
        global nbDock
        global portC
        global next_max
        global clientD
        global delta_Moy
        global atom
        global nexPort
        global portInUse
        global portSleep

        count += 1  # ------------------------------------------------additione le compteur de message
        data = self.request.recv(1024) # -----------------------------lis le msg
        ret,delta = send_msg(data,portInUse[count%len(portInUse)]) # -envoie le msg au bon worker
        delta_Moy.append(delta) #-------------------------------------ajout le lag a la memoire
        delta_Moy_calc = sum(delta_Moy)/len(delta_Moy) # -------------calcule le lag moyen
        print(delta_Moy_calc)
        if(len(delta_Moy)>5): # --------------------------------------ne garde que les 5 dernier lag
            delta_Moy.pop(0)
        if(delta_Moy_calc > next_max and not atom): # ----------------le lag depace la valeur critique
            atom = True # --------------------------------------------entree zone atomique            

            next_max = next_max + 3 # --------------------------------augmente la valeur de la prochaine zone critique
            portInUse.append(portSleep) # ----------------------------le docker en veille passe actif
            print("start Docker")
            clientD.containers.run("python:vsr",f'python3 worker.py {nexPort}', remove=True, ports={nexPort:nexPort}, detach=True) # cree un nouveau docker
            print("Docker started")
            portSleep = nexPort
            nexPort += 1
            nbDock = nbDock + 1
            atom = False # -------------------------------------------sortie zone atomique
            
        if( delta_Moy_calc < (next_max - 5) and nbDock >= 2 and not atom): # si la valeur du lag a suffisament baisser et qu'il reste plus de 1 docker
            atom = True
            print("stop Docker")
            next_max = next_max - 3
            docker_list = clientD.containers.list(ignore_removed = True)
            clientD.api.stop( docker_list[0].id, timeout= None)
            portSleep = portInUse[len(portInUse)-1]
            portInUse.pop(len(portInUse)-1)
            nbDock = nbDock - 1
            print("Docker closed")
            atom = False
        
        if data == b'quit':
            os._exit(0)
        else:
            self.request.sendall(ret)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def main():
    global server
    global portC
    global clientD
    global nexPort
    global portSleep
    global portInUse

    sem_init()
    
    count = 0
    
    
    try:
        portC = int(sys.argv[1])
    except:
        portC = 9090

    clientD = docker.from_env()
    nexPort = portC + 3
    portSleep = portC + 2
    portInUse.append(portC+1)
    
    print(portC)
    print(f'python3 worker.py {portC+1}')
    

    # un docker est gardé en avance affin qu'il sois de suite utilisé, et ne pas devoir attendre la création d'un nouveau 
    clientD.containers.run("python:vsr",f'python3 worker.py {portC+1}',remove=True, ports={portC+1:portC+1}, detach=True) # docker utilisé
    clientD.containers.run("python:vsr",f'python3 worker.py {portC+2}',remove=True, ports={portC+2:portC+2}, detach=True) # docker en veille



    server = ThreadedTCPServer(('0.0.0.0', portC), ThreadedTCPRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.shutdown()      
    server.socket.close()

        

if __name__ == '__main__':

    main()
