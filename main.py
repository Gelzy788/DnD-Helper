import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.uic import loadUi
from config import *
import requests


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('ui_files\\main_screen.ui', self)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.main_screen = loadUi('ui_files\\main_screen.ui')
        self.default_screen = loadUi('ui_files\\default_screen.ui')
        self.login_screen = loadUi('ui_files\\login_screen.ui')
        self.registration_screen = loadUi('ui_files\\registration_screen.ui')
        self.profile_screen = loadUi('ui_files\\profile_screen.ui')

        # Добавляем интерфейсы в QStackedWidget
        self.stacked_widget.addWidget(self.main_screen)
        self.stacked_widget.addWidget(self.default_screen)
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.registration_screen)
        self.stacked_widget.addWidget(self.profile_screen)

        # Подключаем кнопку из первого интерфейса к функции переключения
        self.main_screen.questionnaires_btn.clicked.connect(
            self.switch_to_questionnaire_screen)
        self.main_screen.friends_btn.clicked.connect(
            self.switch_to_friends_screen)
        self.main_screen.groups_btn.clicked.connect(
            self.switch_to_groups_screen)
        self.main_screen.reg_btn.clicked.connect(
            self.switch_to_registration_screen)
        self.main_screen.login_btn.clicked.connect(
            self.switch_to_login_screen)

        self.default_screen.to_main_btn.clicked.connect(
            self.switch_to_main_screen)

        self.login_screen.to_main_btn.clicked.connect(
            self.switch_to_main_screen)
        self.login_screen.login_btn.clicked.connect(
            self.login)

        self.registration_screen.to_main_btn.clicked.connect(
            self.switch_to_main_screen)
        self.registration_screen.reg_btn.clicked.connect(
            self.register)

        self.main_screen.account_btn.clicked.connect(
            self.profile_data)

        self.profile_screen.main_screen_btn.clicked.connect(
            self.switch_to_main_screen)

    def switch_to_main_screen(self):
        self.stacked_widget.setCurrentWidget(self.main_screen)

    def switch_to_questionnaire_screen(self):
        self.stacked_widget.setCurrentWidget(self.default_screen)

    def switch_to_groups_screen(self):
        self.stacked_widget.setCurrentWidget(self.default_screen)

    def switch_to_friends_screen(self):
        self.stacked_widget.setCurrentWidget(self.default_screen)

    def switch_to_account_screen(self):
        self.stacked_widget.setCurrentWidget(self.default_screen)

    def switch_to_registration_screen(self):
        self.stacked_widget.setCurrentWidget(self.registration_screen)

    def switch_to_login_screen(self):
        self.stacked_widget.setCurrentWidget(self.login_screen)

    def register(self):
        email = self.registration_screen.email_le.text()
        password = self.registration_screen.password_le.text()
        username = self.registration_screen.username_le.text()

        response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/registration', json={'email': email, 'password': password, 'username': username})

        if response.status_code == 200:
            self.registration_screen.reg_res.setText('registration successful')
            print('registration successful')
        else:
            self.registration_screen.reg_res.setText('registration failed')
            print('registration failed')

    def login(self):
        email = self.login_screen.email_le.text()
        password = self.login_screen.password_le.text()

        response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/login', json={'email': email, 'password': password})

        if response.status_code == 200:
            self.login_screen.login_res.setText('login successful')
            self.token = response.json().get('token')
            with open('token.txt', 'w') as f:
                f.write(self.token)
            print('login successful')
        else:
            self.login_screen.login_res.setText('login failed')
            print('login failed')

    def profile_data(self):
        if hasattr(self, 'token'):
            # print(self.token, 'token')
            response = requests.get(
                f'http://{IP_ADDRESS}:{PORT}/profile', headers={'Authorization': f'Bearer {self.token}'})
            data = response.json()
            self.stacked_widget.setCurrentWidget(self.profile_screen)
            self.profile_screen.user_id_label.setText(str(data['id']))
            self.profile_screen.username_label.setText(data['username'])
            self.profile_screen.email_label.setText(data['email'])
            self.profile_screen.password_label.setText(data['password'])
        else:
            print('token not found')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
