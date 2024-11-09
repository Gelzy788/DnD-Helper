import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel
import requests


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Login')

        self.layout = QVBoxLayout()

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText('Email')
        self.layout.addWidget(self.email_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_input)

        self.login_button = QPushButton('Login', self)
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

        self.message_label = QLabel('', self)
        self.layout.addWidget(self.message_label)

        self.setLayout(self.layout)

    def login(self):
        email = self.email_input.text()
        password = self.password_input.text()

        response = requests.post(
            'http://192.168.1.4:5000/login', json={'email': email, 'password': password})

        if response.status_code == 200:
            self.message_label.setText('Login successful')
        else:
            self.message_label.setText('Login failed')

    def register(self):
        email = self.email_input.text()
        password = self.password_input.text()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
