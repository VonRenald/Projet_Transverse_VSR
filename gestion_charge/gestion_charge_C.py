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



sem = None
serverC = None
serverW = None

count = 0

portC = 0
nexPort = 0
portSleep = 0
portInUse = []

nbDock = 1
next_max = 3

clientD = None

delta_Moy = [0]

t2_after_stop_docker = time.time()
t1_after_stop_docker = t2_after_stop_docker - 60

atom = False

def send_msg(msg, port, wait_answer = True):
    
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
    
    def handle(self):
        global count
        global nbDock
        global portC
        global next_max
        global clientD
        global delta_Moy
        global t1_after_stop_docker
        global t2_after_stop_docker
        global atom
        global nexPort
        global portInUse
        global portSleep

        count += 1
        t2_after_stop_docker = time.time()
        data = self.request.recv(1024)
        ret,delta = send_msg(data,portInUse[count%len(portInUse)])
        delta_Moy.append(delta)
        delta_Moy_calc = sum(delta_Moy)/len(delta_Moy)
        print(delta_Moy_calc)
        if(len(delta_Moy)>5):
            delta_Moy.pop(0)
        if(delta_Moy_calc > next_max and not atom):# and t2_after_stop_docker - t1_after_stop_docker > 60):
            atom = True
            # print(nbDock, next_max,portC+2+nbDock, count)
            

            next_max = next_max + 3
            print("start Docker")
            clientD.containers.run("python:vsr",f'python3 worker.py {nexPort}',remove=True, ports={nexPort:nexPort}, detach=True)
            print("Docker started")
            portInUse.append(portSleep)
            portSleep = nexPort
            nexPort += 1
            nbDock = nbDock + 1
            # print(nbDock, next_max,portC+2+nbDock, count)
            atom = False
            
        if( delta_Moy_calc < (next_max - 5) and nbDock >= 2 and not atom):
            atom = True
            print("stop Docker")
            next_max = next_max - 3
            docker_list = clientD.containers.list(ignore_removed = True)
            clientD.api.stop( docker_list[0].id, timeout= None)
            portSleep = portInUse[len(portInUse)-1]
            portInUse.pop(len(portInUse)-1)
            nbDock = nbDock - 1
            print("Docker closed")
            # t1_after_stop_docker = t2_after_stop_docker
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
    clientD.containers.run("python:vsr",f'python3 worker.py {portC+1}',remove=True, ports={portC+1:portC+1}, detach=True)
    clientD.containers.run("python:vsr",f'python3 worker.py {portC+2}',remove=True, ports={portC+2:portC+2}, detach=True)



    server = ThreadedTCPServer(('0.0.0.0', portC), ThreadedTCPRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    print("lalala")
    server.shutdown()      
    server.socket.close()

        

if __name__ == '__main__':

    main()
