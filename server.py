import socket
from _thread import *
import pickle

from game import Game
from player import Player

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = "192.168.0.245"
port = 5555

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen()
print("Waiting for a connection")

connections = 0
idCount = 0
games = {}
players = []

def init_players(p):
    global players 
    player = Player(p)
    players.append(player)

def threaded_client(conn, p, gameId):
    global idCount, players
    conn.send(str.encode(str(p)))

    reply = ""
    while True:
        try:
            data = conn.recv(4096*4).decode()

            if gameId in games:
                game = games[gameId]
                cur_player = players[p]
                if not data:
                    print("No data")
                    break
                else:

                    datas = data.split(" ")
                    if data == "reset":
                        print("Reset game")
                        game.reset()

                    if data == "reset match":
                        game.end_match()
                        game.reset_match()

                    if datas[0] == "input" and datas[1] != "":
                        text = datas[1]
                        if text == "back":
                            if len(cur_player.input) > 0:
                                cur_player.input.pop()
                        elif text != "back":
                            if len(cur_player.input) < 3:
                                cur_player.input.append(text)

                    if data == "locked":
                        cur_player.locked = True
                            
                    reply = game
                    conn.sendall(pickle.dumps(reply))

            else:
                print("No game")
                break
        except socket.error as e:
            print(e)
            break
    print("Lost connection")
    try:
        if p == 0:
            del games[gameId]
            print("Closing game", gameId)
    except:
        pass
    idCount -= 1
    players.pop()
    conn.close()

def main():
    global connections, idCount, players
    if connections < 5:
        connections += 1
        while True:
            conn, addr = s.accept()
            print("Connected to: ", addr)

            idCount += 1
            p = idCount - 1
            gameId = (idCount -1) // 5
            init_players(p)
            if idCount == 1:
                games[gameId] = Game(gameId, players)
                print("Creating a new game...")
            else:
                games[gameId].players = players
            
            start_new_thread(threaded_client, (conn, p, gameId))

                
if __name__ == "__main__":
    main()
