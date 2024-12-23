from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QPushButton, QInputDialog, QMessageBox
from PyQt6.uic import loadUi
import requests
from my_config import *


class LoginManager(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        # self.load_tokens()

    def init_ui(self):
        loadUi('data/ui_files/login_screen.ui', self)

        self.login_btn.clicked.connect(self.login)
        self.to_main_btn.clicked.connect(self.go_back)

    # Вход в профиль
    def login(self):
        email = self.email_le.text()
        password = self.password_le.text()

        response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/login', json={'email': email, 'password': password})

        if response.status_code == 200:
            self.login_res.setText('login successful')
            access_token = response.json().get('access_token')
            refresh_token = response.json().get('refresh_token')

            with open("tokens.txt", 'w') as f:
                print(access_token, '>>', refresh_token)
                f.write(access_token)
                f.write('\n')
                f.write(refresh_token)
            # with open("../../tokens.txt", 'r') as f:
            #     print(access_token, '>>', refresh_token)
            #     print(f.readlines())
            print('login successful')
        else:
            self.login_res.setText('login failed')

        # with open("tokens.txt", 'r') as f:
        #     print(access_token, '>>', refresh_token)
        #     print(f.readlines())

    # Переход на главный экран
    def go_back(self):
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.main_window)
