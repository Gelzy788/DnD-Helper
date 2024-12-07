from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.uic import loadUi
from my_config import *
import requests


class RegisterManager(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        loadUi('data/ui_files/registration_screen.ui', self)
        self.email_le.clear()
        self.password_le.clear()
        self.username_le.clear()
        # Кнопки
        self.to_main_btn.clicked.connect(self.go_back)
        self.reg_btn.clicked.connect(self.register)

    # Регистрация пользователя
    def register(self):
        email = self.email_le.text()
        password = self.password_le.text()
        username = self.username_le.text()

        if email != '' and password != '' and username != '':
            response = requests.post(
                f'http://{IP_ADDRESS}:{PORT}/registration', json={'email': email, 'password': password, 'username': username})

            if response.status_code == 200:
                self.reg_res.setText(
                    'registration successful')
                print('registration successful')
            else:
                self.reg_res.setText('registration failed')
                print('registration failed')
        else:
            self.reg_res.setText('registration failed')
            print('registration failed')

    # Переход на главный экран
    def go_back(self):
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.main_window)
