import sys
import socket
from multiprocessing import Process
import time

host = '127.0.0.1'
try:
    port = int(sys.argv[1])
except:
    port = 9090

nb_messages = 1000
sleeping_time = .1

def send_msg(msg, wait_answer = True):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((host,port))
        client.send(msg)
        if wait_answer:
            response = client.recv(1024)
            print(response)

jobs = [Process(target = send_msg, args = (b'go', ))
        for _ in range(nb_messages)]
for j in jobs:
    j.start()
    time.sleep(sleeping_time)
for j in jobs:
    j.join()
