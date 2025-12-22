import socket

ROBOT_IP = "172.18.26.112"   # ⚠️ 改成树莓派 IP
PORT = 60010

s = socket.socket()
s.connect((ROBOT_IP, PORT))
s.sendall(b"wave\n")
s.close()
