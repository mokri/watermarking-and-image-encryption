#This is for clint
import socket
import cv2
import time
c = socket.socket()
q = "127.0.0.1" # input("Enter the ip addess from where you want to receive the image")
p = 5555 # int(input("Enter the port number"))
r = "png" # input("Enter the extension of your received file - jpg , png , bmp")
s = "pythonimage123." + r
print(s)
condition = True
c.connect((q,p))
f = open(s,"wb")
while condition:
    image = c.recv(1024)
    if str(image) == "b''":
        condition = False
    f.write(image)
