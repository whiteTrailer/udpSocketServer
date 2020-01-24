import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json

clients_lock = threading.Lock()
connected = 0

clients = {}

#  message loop 
def connectionLoop(sock):
   while True:
      data, addr = sock.recvfrom(1024)
      data = str(data)
      if addr in clients:
         if 'heartbeat' in data:
            clients[addr]['lastBeat'] = datetime.now()
      else:
         # new client
         if 'connect' in data:
            clients[addr] = {}
            clients[addr]['lastBeat'] = datetime.now()
            clients[addr]['color'] = {"RED": random.random(), "GREEN": random.random(), "BLUE": random.random()}
            
             message = {"cmd": 0,"players":[{"id":str(addr), "color": clients[addr]['color']}]}
            m = json.dumps(message)
            for c in clients:
               if c != addr :
                  print(m)
                  sock.sendto(bytes(m,'utf8'), (c[0],c[1]))
            
            print('Player is connected')
            Spawn = {"cmd": 2, "players": []}
            for c in clients:
               player = {}
               player['id'] = str(c)
               player['color'] = clients[c]['color']
             Spawn['players'].append(player)
            playerInfo=json.dumps(Spawn)
            print(playerInfo)
            sock.sendto(bytes(playerInfo,'utf8'), (addr[0],addr[1]))


def cleanClients(sock):
   while True:
      deleteMessage = {"cmd": 2,"players":[]}
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
            print('Player Left Clients: ', c)
            player = {}
            player['id'] = str(c)
            player['color'] = clients[c]['color']
            deleteMessage['players'].append(player)
            clients_lock.acquire()
            del clients[c]
            clients_lock.release()

      dm = json.dumps(deleteMessage)
      for f in clients:
         sock.sendto(bytes(dm,'utf8'), (f[0],f[1]))

      time.sleep(1)


def gameLoop(sock):
   while True:
      GameState = {"cmd": 1, "players": []}
      clients_lock.acquire()
      for c in clients:
         player = {}
         clients[c]['color'] = {"RED": random.random(), "GREEN": random.random(), "BLUE": random.random()}
         player['id'] = str(c)
         player['color'] = clients[c]['color']
         GameState['players'].append(player)
      s=json.dumps(GameState)
      print(s)
      for c in clients:
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      clients_lock.release()
      time.sleep(1)

def main():
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(cleanClients,(s,))
   while True:
      time.sleep(1)

if __name__ == '__main__':
   main()