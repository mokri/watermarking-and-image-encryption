import sys, time

from PyQt5.QtGui import QCursor, QPixmap
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication
import socket
from threading import Thread
from socketserver import ThreadingMixIn
import cv2 as cv

tcpClientA = None


class Window(QDialog):
    def __init__(self):
        super().__init__()
        self.flag = 0

        self.connection_group = QGroupBox(self)
        self.connection_group.setGeometry(QtCore.QRect(30, 10, 700, 101))
        self.connection_group.setTitle('Connection')

        self.client_label = QLabel('CLIENT')
        self.line = QLineEdit()
        self.ip_label = QLabel('IP')
        self.port_label = QLabel('PORT')

        self.ip_text_field = QTextEdit()
        self.ip_text_field.setText('127.0.0.1')
        self.ip_text_field.setEnabled(False)

        self.port_text_field = QTextEdit()
        self.port_text_field.setText('5555')

        self.connection_box = QGridLayout()
        self.connection_group.setLayout(self.connection_box)
        self.connection_box.addWidget(self.client_label, 0, 0)
        self.connection_box.addWidget(self.ip_label, 1, 1)
        self.connection_box.addWidget(self.ip_text_field, 1, 2)
        self.connection_box.addWidget(self.port_label, 2, 1)
        self.connection_box.addWidget(self.port_text_field, 2, 2)
        self.connection_box.setRowStretch(4, 1)

        #
        # Image Group Box
        #

        self.button_style = "*{color: blue;" \
                            "padding: 5px 20px;" \
                            "text-align: center;" \
                            "text-decoration: none;" \
                            "font-size: 10px;" \
                            "margin: 2px 2px;}" \
                            "*:hover{background-color: #8ecae6;" \
                            "color: #023047;}"

        self.image_group = QGroupBox(self)
        self.image_group.setGeometry(QtCore.QRect(30, 130, 341, 100))
        self.image_group.setTitle('Image')

        # save image

        self.save_image = QPushButton()
        self.save_image.setText('Enregistrer l\'Image')
        self.save_image.setStyleSheet(self.button_style)
        self.save_image.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        self.load_image = QPushButton()
        self.load_image.setText('Charger l\'Image crypte')
        self.load_image.setStyleSheet(self.button_style)
        self.load_image.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        # image group box

        self.image_box = QGridLayout()
        self.image_group.setLayout(self.image_box)
        self.image_box.addWidget(self.load_image, 0, 0)
        self.image_box.addWidget(self.save_image, 1, 0)

        #
        # Image View
        #

        self.widget = QWidget()
        self.image_tab = QTabWidget(self)
        self.image_label = QLabel('image')
        self.image_watermark_box = QGridLayout()
        self.widget.setLayout(self.image_watermark_box)

        self.image_watermark_box.addWidget(self.image_label, 0, 0)
        self.tab_1 = self.widget
        # self.tab_1 = self.watermark_label
        # self.tab_2 = self.watermark_label

        self.image_tab.addTab(self.tab_1, 'Image')
        # self.image_tab.addTab(self.tab_2, 'Image Chiffree')
        self.image_tab.setGeometry(QtCore.QRect(400, 130, 341, 550))

        #
        # Chiffrement / Dechiffrement
        #

        self.algo_label = QLabel('Selectioner un algorithm :')
        self.algo_comboBox = QComboBox()
        self.algo_comboBox.addItem('Plain')
        self.algo_comboBox.addItem('DES')
        self.algo_comboBox.addItem('DESede')
        self.algo_comboBox.addItem('AES')
        self.algo_comboBox.addItem('RC2')
        self.algo_comboBox.addItem('RC4')
        self.algo_comboBox.addItem('Blowfish')
        self.algo_comboBox.addItem('XOR')
        self.algo_comboBox.addItem('RSA')

        self.generate_key_button = QPushButton()
        self.generate_key_button.setText('Generer la cle')
        self.crypt_key_text_field = QLineEdit()
        self.crypt_key_text_field.setText('KEY : ')
        # self.crypt_key_text_field.setReadOnly(True)

        self.decrypt_key_button = QPushButton()
        self.decrypt_key_button.setText('Decrypter')

        self.crypt_group = QGroupBox(self)
        self.crypt_group.setGeometry(QtCore.QRect(30, 260, 341, 280))
        self.crypt_group.setTitle('Chiffrement / Dechiffrement')

        self.crypt_box = QGridLayout()
        self.crypt_group.setLayout(self.crypt_box)

        self.crypt_box.addWidget(self.algo_label, 0, 0)
        self.crypt_box.addWidget(self.algo_comboBox, 0, 1)
        self.crypt_box.addWidget(self.generate_key_button, 1, 0, 1, 2)
        self.crypt_box.addWidget(self.crypt_key_text_field, 2, 0, 1, 2)
        self.crypt_box.addWidget(self.decrypt_key_button, 4, 0, 1, 2)
        self.crypt_box.setRowStretch(5, 0)
        self.crypt_box.setSpacing(5)

        #
        # send KEY
        #

        self.load_image.clicked.connect(self.display_image)
        self.save_image.clicked.connect(self.save_crypted_image)

        # self.decrypt_key_button.clicked.connect(self.send_key)

        # self.connectBtn = QPushButton('connecter', self)

        # self.chatTextField = QLineEdit(self)
        # self.chatTextField.resize(180, 100)
        # self.chatTextField.move(10, 350)
        # self.btnSend = QPushButton("Send", self)
        # self.btnSend.resize(480, 30)
        # self.btnSendFont = self.btnSend.font()
        # self.btnSendFont.setPointSize(15)
        # self.btnSend.setFont(self.btnSendFont)
        # self.btnSend.move(10, 460)
        # self.btnSend.setStyleSheet("background-color: #F7CE16")
        # self.btnSend.clicked.connect(self.send)
        #
        # self.chatBody = QVBoxLayout(self)
        # # self.chatBody.addWidget(self.chatTextField)
        # # self.chatBody.addWidget(self.btnSend)
        # # self.chatWidget.setLayout(self.chatBody)
        # splitter = QSplitter(QtCore.Qt.Vertical)
        #
        # self.chat = QTextEdit()
        # self.chat.setReadOnly(True)
        #
        # splitter.addWidget(self.chat)
        # splitter.addWidget(self.chatTextField)
        # splitter.setSizes([400, 100])
        #
        # splitter2 = QSplitter(QtCore.Qt.Vertical)
        # splitter2.addWidget(splitter)
        # splitter2.addWidget(self.btnSend)
        # splitter2.setSizes([200, 10])
        #
        # self.chatBody.addWidget(splitter2)
        #
        self.setWindowTitle("Client Application")
        self.resize(750, 700)

    # def send_key(self):
    #
    #
    #     text = self.crypt_key_text_field.text()
    #     #text = self.chatTextField.text()
    #     # font = self.chat.font()
    #     # font.setPointSize(13)
    #     # self.chat.setFont(font)
    #     textFormatted = '{:>80}'.format(text)
    #     #self.crypt_key_text_field.append(textFormatted)
    #     self.crypt_key_text_field.setText(textFormatted)
    #     tcpClientA.send(text.encode())
    #     #self.crypt_key_text_field.setText("")

    def display_image(self):
        try:
            self.pixmap = QPixmap('pythonimage123.png')


            self.image_label.setPixmap(self.pixmap.scaled(330, 540))
        except Exception:
            print('loading image error')

    def save_crypted_image(self):
        name = QFileDialog.getSaveFileName(self, 'Save File')
        name = name[0]
        image = cv.imread('pythonimage123.png')
        # text = self.textEdit.toPlainText()

        if name.endswith('.png'):
            print(name)
            cv.imwrite(name, image)

        else:
            print(name)
            name += '.png'
            cv.imwrite(name, image)

        # file.write(text)
        # file.close()


class ClientThread(Thread):
    def __init__(self, window):
        Thread.__init__(self)
        self.window = window

    def run(self):
        print('client thread')
        host = '127.0.0.1'  # socket.gethostname()
        port = 5555
        BUFFER_SIZE = 2000
        global tcpClientA
        tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpClientA.connect((host, port))
        f = open('pythonimage123.png', "wb")
        condition = True
        mystr = ''

        while condition:

            # data = tcpClientA.recv(BUFFER_SIZE)
            image = tcpClientA.recv(1024)

            if not str(image).startswith('b\'KEY'):
                # print(data.decode("utf-8"))

                if str(image) == "b''":
                    condition = False
                    print('empty')
                f.write(image)
                mystr = str(image)
                mystr = mystr[1: -1]

                if 'END_IMAGE_SENDING' in mystr:
                    # print(mystr)
                    break

                # print('receiving image')
            else:
                # print(image)
                window.crypt_key_text_field.setText(image.decode("utf-8"))
        # print(mystr)
        f.close()

        tcpClientA.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    clientThread = ClientThread(window)
    clientThread.start()
    window.exec()
    sys.exit(app.exec_())
