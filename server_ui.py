import datetime
import socket
import sys
from threading import Thread

import cv2 as cv
from PyQt5 import QtCore
from PyQt5.QtGui import QCursor, QPixmap
from PyQt5.QtWidgets import *
from io import BytesIO
from encryption.RSA import AES

conn = None


class Window(QDialog):
    def __init__(self):
        super().__init__()
        self.flag = 0

        self.connection_group = QGroupBox(self)
        self.connection_group.setGeometry(QtCore.QRect(30, 10, 700, 101))
        self.connection_group.setTitle('Connection')

        self.client_label = QLabel('SERVEUR')
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
        self.image_group.setGeometry(QtCore.QRect(30, 130, 341, 250))
        self.image_group.setTitle('Image')

        # load image

        self.load_image = QPushButton()
        self.load_image.setText('Charger Une Image')
        self.load_image.setStyleSheet(self.button_style)
        self.load_image.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        #  load watermark

        self.load_watermark = QPushButton()
        self.load_watermark.setText('Charger Watermark')
        self.load_watermark.setStyleSheet(self.button_style)
        self.load_watermark.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        # send image

        self.send_image = QPushButton()
        self.send_image.setText('Envoyer l\'Image')
        self.send_image.setStyleSheet(self.button_style)
        self.send_image.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        # opacity slider

        self.opacity_label = QLabel('Opacity :')
        self.opacity_slider = QSlider(valueChanged=self.onValueChanged)
        self.opacity_slider.setOrientation(QtCore.Qt.Horizontal)
        self.opacity_slider.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.opacity_slider.setRange(0, 10)
        # self.opacity_slider.setTickInterval(100)
        self.opacity_slider.setSingleStep(1)

        # image group box

        self.image_box = QGridLayout()
        self.image_group.setLayout(self.image_box)
        self.image_box.addWidget(self.load_image, 0, 0, 1, 2)
        self.image_box.addWidget(self.load_watermark, 1, 0, 1, 2)
        self.image_box.addWidget(self.opacity_label, 2, 0)
        self.image_box.addWidget(self.opacity_slider, 2, 1)
        self.image_box.addWidget(self.send_image, 4, 0, 1, 2)
        self.image_box.setRowStretch(5, 0)
        self.image_box.setSpacing(0)

        #
        # Image View
        #

        self.widget = QWidget()
        self.image_tab = QTabWidget(self)

        self.image_label = QLabel('image')
        self.watermark_label = QLabel('watermark')

        self.image_watermark_box = QGridLayout()
        self.widget.setLayout(self.image_watermark_box)

        self.image_watermark_box.addWidget(self.image_label, 0, 0)

        self.image_watermark_box.addWidget(self.watermark_label, 0, 0)

        self.tab_1 = self.widget
        self.tab_2 = QWidget()
        # self.tab_2 = self.watermark_label

        self.image_tab.addTab(self.tab_1, 'Image')
        self.image_tab.addTab(self.tab_2, 'Image Chiffree')
        self.image_tab.setGeometry(QtCore.QRect(400, 130, 341, 550))

        #
        # Chiffrement / Dechiffrement
        #

        self.algo_label = QLabel('Selectioner un algorithm :')
        self.algo_comboBox = QComboBox()

        self.algo_comboBox.addItem('AES')


        self.generate_key_button = QPushButton()
        self.generate_key_button.setText('Generer la cle')
        self.crypt_key_text_field = QLineEdit()
        self.crypt_key_text_field.setText('KEY : ')
        # self.crypt_key_text_field.setReadOnly(True)

        self.crypt_key_button = QPushButton()
        self.crypt_key_button.setText('Crypter')

        self.crypt_group = QGroupBox(self)
        self.crypt_group.setGeometry(QtCore.QRect(30, 400, 341, 280))
        self.crypt_group.setTitle('Chiffrement / Dechiffrement')

        self.crypt_box = QGridLayout()
        self.crypt_group.setLayout(self.crypt_box)

        self.crypt_box.addWidget(self.algo_label, 0, 0)
        self.crypt_box.addWidget(self.algo_comboBox, 0, 1)
        self.crypt_box.addWidget(self.generate_key_button, 1, 0, 1, 2)
        self.crypt_box.addWidget(self.crypt_key_text_field, 2, 0, 1, 2)
        self.crypt_box.addWidget(self.crypt_key_button, 3, 0, 1, 2)
        self.crypt_box.setRowStretch(5, 0)
        self.crypt_box.setSpacing(5)

        #
        # SEND KEY
        #

        self.send_image.clicked.connect(self.send_image_key)

        #
        # load IMAGE / WATERMARK

        #

        self.load_image.clicked.connect(self.image_loader)
        self.load_watermark.clicked.connect(self.watermark_loader)

        #
        # crypt watermarked image and send crypting key
        #

        # self.crypt_key_button.clicked.connect(self.send_key)
        self.crypt_key_button.clicked.connect(lambda: self.watermarking(self.opacity))

        # self.chatTextField = QLineEdit(self)
        # self.chatTextField.resize(480, 100)
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
        # self.chatBody.addWidget(self.chatTextField)
        # self.chatBody.addWidget(self.btnSend)
        # self.chatWidget.setLayout(self.chatBody)
        # splitter = QSplitter(QtCore.Qt.Vertical)

        # self.chat = QTextEdit()
        # self.chat.setReadOnly(True)
        # self.chatLayout=QVBoxLayout()
        # self.scrollBar=QScrollBar(self.chat)
        # self.chat.setLayout(self.chatLayout)

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

        self.setWindowTitle("Server Application")
        self.resize(750, 700)

    def image_loader(self):
        filename = QFileDialog.getOpenFileName(filter='*.png *.jpg *jpeg *bmp')
        path = filename[0]
        try:
            self.original_image_file = cv.imread(path, cv.IMREAD_UNCHANGED)
            self.i_h, self.i_w, c = self.original_image_file.shape
            self.original_image_file = cv.cvtColor(self.original_image_file, cv.COLOR_BGR2BGRA)
        except Exception:
            print('loading image error')

        self.pixmap = QPixmap(path)
        self.image_label.setPixmap(self.pixmap.scaled(330, 540))

    def watermark_loader(self):
        filename = QFileDialog.getOpenFileName(filter='*.png *.jpg *.jpeg *.bmp')
        path = filename[0]
        self.opacity = 1.0
        try:
            self.watermark_file = cv.imread(path, cv.IMREAD_UNCHANGED)
            self.watermark_file = cv.resize(self.watermark_file, (100, 100), interpolation=cv.INTER_AREA)

        except Exception:
            print('error loading water mark')

        # cv.circle(self.original_image_file, (top[0], top[1]), 10, (0, 255, 0), -1)
        # cv.circle(self.original_image_file, (bottom[0], bottom[1]), 10, (0, 255, 0), -1)
        # Get ROI
        # roi = self.original_image_file[top[1]: bottom[1], top[0]: bottom[0]]

        self.pixmap_watermark = QPixmap(path)
        self.watermark_label.setPixmap(self.pixmap_watermark.scaled(100, 100))

    def watermarking(self, opacity):

        w_h, w_w, c = self.watermark_file.shape
        center = (int(self.i_h / 2), int(w_h / 2))
        top = (center[1] - int(w_w / 2), center[0] - int(w_h / 2))
        bottom = (center[1] + int(w_w / 2), center[0] + int(w_h / 2))

        # You may need to convert the color.
        # img = cv.cvtColor(self.watermark_file, cv.COLOR_BGR2RGB)
        # im_pil = Image.fromarray(img)
        #
        # im_pil.putalpha(opacity)

        # For reversing the operation:
        # im_np = np.asarray(im_pil)

        # ROI

        roi = self.original_image_file[top[1]: bottom[1], top[0]: bottom[0]]
        watermarked_image = self.original_image_file.copy()

        result = cv.addWeighted(roi, 1.0, self.watermark_file, opacity, 0)

        watermarked_image[top[1]: bottom[1], top[0]: bottom[0]] = result

        watermarked_image_name = f"image_crypted.png"

        #watermarked_image = bytearray(watermarked_image)
        key = 27
        fin = open('ni.png', 'wb')

        # for index, values in enumerate(watermarked_image):
        #     watermarked_image[index] = values ^ key

        fin.write(watermarked_image)
        fin.close()

        cv.imwrite(watermarked_image_name, watermarked_image)
        self.send_key()

    def onValueChanged(self, value):
        # creating a opacity effect
        self.opacity = float(value / 10)
        print(self.opacity)
        self.opacity_effect = QGraphicsOpacityEffect()

        print(self.opacity)
        # setting opacity level
        self.opacity_effect.setOpacity(value / 10)

        # adding opacity effect to the label
        self.watermark_label.setGraphicsEffect(self.opacity_effect)

    def send_image_key(self):
        image = open('image_crypted.png', "rb")
        test = 1
        global conn

        file_like = BytesIO(b'END_IMAGE_SENDING')
        if conn != 0:
            for i in image:
                conn.send(i)
                ##print('sending : ', i)

            conn.send(file_like.read())
            # image.close()

    def send_key(self):
        text = self.crypt_key_text_field.text()
        # text = self.chatTextField.text()
        # font = self.chat.font()
        # font.setPointSize(13)
        # self.chat.setFont(font)
        textFormatted = '{:>80}'.format(text)
        # self.crypt_key_text_field.append(textFormatted)
        self.crypt_key_text_field.setText(textFormatted)
        global conn
        print(text.encode("utf-8"))
        conn.send(text.encode("utf-8"))
        # self.crypt_key_text_field.setText("")


class ServerThread(Thread):
    def __init__(self, window):
        Thread.__init__(self)
        self.window = window

    def run(self):
        TCP_IP = '127.0.0.1'
        TCP_PORT = 5555
        BUFFER_SIZE = 20
        tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcpServer.bind((TCP_IP, TCP_PORT))
        threads = []

        tcpServer.listen(4)
        while True:
            print("Multithreaded Python server : Waiting for connections from TCP clients...")
            global conn
            (conn, (ip, port)) = tcpServer.accept()
            newthread = ClientThread(ip, port, window)
            newthread.start()
            threads.append(newthread)

        for t in threads:
            t.join()


class ClientThread(Thread):

    def __init__(self, ip, port, window):
        Thread.__init__(self)
        self.window = window
        self.ip = ip
        self.port = port
        print("[+] New server socket thread started for " + ip + ":" + str(port))

    def run(self):
        print('client thread in server')
        while True:
            # (conn, (self.ip,self.port)) = serverThread.tcpServer.accept()
            global conn
            data = conn.recv(2048)
            # window.crypt_key_text_field.append(data.decode("utf-8"))
            window.crypt_key_text_field.setText(data.decode("utf-8"))
            print(data)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = Window()
    serverThread = ServerThread(window)
    serverThread.start()
    window.exec()

    sys.exit(app.exec_())
