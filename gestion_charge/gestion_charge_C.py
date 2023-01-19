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

portW = 9091
nbDock = 1
next_max = 3

try:
    portC = int(sys.argv[1])
except:
    portC = 9090

clientD = docker.from_env()
print(portW)
print(f'python3 worker.py {portW}')
clientD.containers.run("python:worker",f'python3 worker.py {portC+1}',remove=True, ports={portC+1:portC+1}, detach=True)
clientD.containers.run("python:worker",f'python3 worker.py {portC+2}',remove=True, ports={portC+2:portC+2}, detach=True)

# client.containers.run("python:worker",'python3 worker.py 9095',remove=True, ports={9095:9095}, detach=True)
# client.containers.run("python:worker",'python3 worker.py 9098',remove=True, ports={9098:9098}, detach=True)

# subprocess.run("docker run --rm -p 9090:9090 python:worker ",stdout=subprocess.PIPE)
# subprocess.run("docker run --rm -p 9095:9090 python:worker ",stdout=subprocess.PIPE)
# subprocess.run("docker run --rm -p 9098:9090 python:worker ",stdout=subprocess.PIPE)


# subprocess.run(["ls"],stdout=subprocess.PIPE)
def send_msg(msg, port,  nbDock, next_max, portC, clientD, wait_answer = True):
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(('127.0.0.1',port))
        t1 = time.time()
        client.send(msg)
        if wait_answer:
            response = client.recv(1024)
            t2 = time.time()
            print("return in ",t2-t1,"- ",end=' ')
            print(response)
            print(next_max,nbDock,next_max)
            if(t2-t1 > next_max):
                print("new docker")
                clientD.containers.run("python:worker",f'python3 worker.py {portC+2+nbDock}',remove=True, ports={portC+2+nbDock:portC+2+nbDock}, detach=True)
                nbDock+=1
                next_max+=3
            return response,nbDock,next_max
    return None,nbDock,next_max

def read_int(filename, default):
    try:
        with open(filename, 'r') as file:
            return int(f.read())
    except:
        return default

# def work():
#     global sem
#     with sem:
#         print('start working', os.getpid());
#         time.sleep(.5)
#         print('end working', os.getpid());

# def manage_request():
#     global sem
#     Process(target = work, args=()).start()

def sem_init():
    global sem
    ## 1 worker per 100MB
    unit = 100*1000*1000
    nb_parallel = read_int('/sys/fs/cgroup/memory.max', 3*unit) // unit
    sem = Semaphore(value = nb_parallel)


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        global count
        global server
        global nbDock
        global next_max
        global portC
        global clientD
        
        count += 1
        print(portC+(count%nbDock)+1)
        data = self.request.recv(1024)
        # print("read - ",end=' ')
        # print(data)
        ret,nbDock,next_max = send_msg(data,portC+(count%nbDock)+1, nbDock, next_max, portC, clientD)
        # if(ret >= 0):
        #     nbDock = d
        #     next_max = m
        # print(nbDock,next_max)
        # if count%3 == 0:
        #     ret = send_msg(data,portW)
        # else :
        #     if count%3 == 1:
        #         ret = send_msg(data,portW2)
        #     else:
        #         ret = send_msg(data,portW3)
        if data == b'quit':
            os._exit(0)
        else:
            self.request.sendall(ret)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def main():
    global server

    sem_init()
    
    count = 0
    
    
    


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
