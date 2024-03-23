import flask
import socket
import os
from werkzeug.utils import secure_filename
import random
import PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
import sys
import threading
import mainwindow
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QMessageBox, QFileDialog
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor
import qrcode
import io
from PyQt5 import QtGui
import setting
import user



def genQrcode(data):
    qr = qrcode.make(data)
    tmp = os.path.join(os.getenv('TEMP'),'同网快传_缓存')
    if not os.path.exists(tmp):
        os.makedirs(tmp)
    tmp_file = os.path.join(tmp, 'qrcode.png')
    qr.save(tmp_file)
    img = QImage(tmp_file)
    pixmap = QPixmap.fromImage(img)
    return pixmap

class SettingWindow(QWidget, setting.Ui_Form):
    def __init__(self):
        super(SettingWindow, self).__init__()
        self.setupUi(self)
        self.toolButton.clicked.connect(self.openFileDialog)
        self.buttonBox.accepted.connect(self.Save)
        self.buttonBox.rejected.connect(self.close)
        if settings.value("savepath", type=str):
            self.lineEdit.setText(settings.value("savepath", type=str))
    def openFileDialog(self):
        # 选择文件夹
        file_path = QFileDialog.getExistingDirectory(self, "选择文件夹", os.getenv("SystemDrive"))
        if file_path:
            self.lineEdit.setText(file_path)
    def Save(self):
        flag = True
        tips = '错误: \n'
        if not os.path.exists(self.lineEdit.text()):
            flag = False
            tips += '保存路径不存在 \n'
        else:
            settings.setValue("savepath", self.lineEdit.text())
        if flag:
            QMessageBox.information(self, "同网快传", "保存成功")
        else:
            QMessageBox.warning(self, "同网快传", tips + '\n部分没有保存成功, 请检查设置')
        self.close()


class MainWindow(QMainWindow,mainwindow.Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.label.setPixmap(genQrcode(site))
        self.lineEdit.setText(site)
        self.pushButton.clicked.connect(lambda: QInputDialog.getText(mainWindow,"同网快传" ,"以下是安全密码:  Ctrl+C 复制", QLineEdit.Normal, safepassword))
        self.pushButton_2.clicked.connect(self.ReSetPassWord)
        self.pushButton_4.clicked.connect(self.openSetting)
        self.pushButton_3.clicked.connect(lambda: openSite('zz'))
        self.actionBy.triggered.connect(lambda: openSite('zz'))
        self.actionGithub.triggered.connect(lambda: openSite('gh'))
        self.pushButton_5.clicked.connect(lambda: openSite('gh'))
    def openSetting(self):
        self.settingWindow = SettingWindow()
        # 设置静态模型
        self.settingWindow.setWindowModality(PyQt5.QtCore.Qt.ApplicationModal)
        self.settingWindow.setWindowFlags(PyQt5.QtCore.Qt.WindowCloseButtonHint)
        self.settingWindow.show()
    def ReSetPassWord(self):
        _safepassword = settings.value("safepassword", type=str)
        text, okPressed = QInputDialog.getText(self, "重设安全密钥 [同网快传]","输入你要设置的安全密钥, 这个密钥由你自己创建\n点击取消可以取消操作", QLineEdit.Normal, _safepassword)
        if not okPressed or text == _safepassword:
            QMessageBox.information(self, "同网快传", "安全密钥未修改")
            return
        globals()['safepassword'] = text
        settings.setValue("safepassword", text)
        QMessageBox.information(self, "同网快传", "安全密钥修改成功")
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '退出', '确认退出吗? \n退出后将无法接收文件传输', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

def openSite(go):
    if go == 'zz': #作者
        os.startfile('https:\\www.52pojie.cn/home.php?mod=space&uid=2104472')
    elif go == 'gh': #github
        os.startfile('https:\\github.com/lh11117/FastSend')

app = flask.Flask(__name__)

@app.route('/')
def index():
    with open('pages/page.html', 'r', encoding='utf-8') as f:
        content = f.read()
    return content


@app.route('/upload', methods=['POST'])
def upload():
    if flask.request.form.get('safepassword')!= safepassword:
        with open('pages/errorwrongpassword.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return content, 400
    if 'file' not in flask.request.files:
        with open('pages/errorcantupload.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return content, 400

    uploaded_file = flask.request.files['file']
    
    # 检查文件是否有效并已选择
    if uploaded_file.filename == '':
        with open('pages/errornofile.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return content, 400

    # 安全处理文件名，防止路径遍历攻击
    filename = uploaded_file.filename

    # 指定保存文件的目录
    upload_dir = settings.value("savepath", type=str)
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # 保存文件
    file_path = os.path.join(upload_dir, filename)
    uploaded_file.save(file_path)

    with open('pages/success.html', 'r', encoding='utf-8') as f:
        content = f.read()
    return content, 200

def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

def FlaskLoop():
    app.run(host=ip, port=6788)


def main():
    global safepassword, ip, site, mainWindow, thread
    if not settings.value("savepath", type=str) or not os.path.exists(settings.value("savepath", type=str)):
        default = os.path.join(os.getenv("SystemDrive") + '/', "同网快传")
        if not os.path.exists(default):
            os.makedirs(default)
        settings.setValue("savepath", default)
    safepassword = settings.value("safepassword", type=str)
    if safepassword == '':
        text, okPressed = QInputDialog.getText(None, "设置安全密钥 [同网快传]","输入你要设置的安全密钥, 这个密钥由你自己创建\n点击取消退出程序 (下次启动仍会提示输入)", QLineEdit.Normal, "")
        if not okPressed or text == '':
            sys.exit()
        safepassword = text
        settings.setValue("safepassword", text)
    ip = get_host_ip()
    site = 'http://'+ip+':6788/'
    mainWindow = MainWindow()
    mainWindow.show()
    #os.startfile('http://'+ip+':6788/')
    thread = threading.Thread(target=FlaskLoop)
    thread.setDaemon(True)
    thread.start()

if __name__ == '__main__':
    Qapp = QApplication(sys.argv)
    settings = QSettings("LcccccccSoft", "FastSend")
    if not settings.value("agree", type=int):
        user_Form = QWidget()
        user_ui = user.Ui_Form()
        user_ui.setupUi(user_Form)
        user_ui.pushButton.clicked.connect(lambda: (settings.setValue("agree", int(user_ui.checkBox.isChecked())),user_Form.close(),main()))
        user_ui.pushButton_2.clicked.connect(lambda: sys.exit())
        user_Form.setFixedSize(user_Form.width(), user_Form.height())
        user_Form.setWindowFlags(PyQt5.QtCore.Qt.WindowCloseButtonHint|PyQt5.QtCore.Qt.WindowStaysOnTopHint)
        user_Form.show()
    else:
        main()
    sys.exit(Qapp.exec_())
    