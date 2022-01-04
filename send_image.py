#This is for socket
from tkinter import *
from tkinter import filedialog
import socket
import cv2
c = 0
q1 = "127.0.0.1" # input("Enter the IP address")
q2 = 5555 # int(input("Enter the port number"))
s = socket.socket()
s.bind((q1,q2))
# data = filedialog.askopenfile(initialdir="/")
# path = str(data.name)
image = open('img.png', "rb")
s.listen(1)
c,address = s.accept()
if c != 0:
    for i in image:
        c.send(i)