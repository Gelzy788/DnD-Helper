from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QPushButton
from PyQt6.uic import loadUi
import requests
from config import *
from my_token import token_required


class ProfileManager(QMainWindow):
    def __init__(self, main_window, access_token, refresh_token):
        super().__init__()
        self.main_window = main_window
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.init_ui()

    # @staticmethod
    # def token_required(func):
    #     def wrapper(self, *args, **kwargs):
    #         try:
    #             with open('tokens.txt', 'r') as f:
    #                 data = f.readlines()
    #                 self.access_token = data[0].strip()
    #                 self.refresh_token = data[1].strip()
    #         except Exception as e1:
    #             print('ОШИБКА')
    #             self.main_window.stacked_widget.setCurrentWidget(
    #                 self.main_window.main_window)
    #         if not self.is_access_token_expiring_soon():
    #             print("Токен истекает, обновляем...")
    #             self.refresh_access_token()
    #         if self.access_token == '':
    #             print("Токен недействителен, перенаправляем на экран входа...")
    #             self.main_window.stacked_widget.setCurrentWidget(
    #                 self.main_window.login_manager)
    #             return
    #         return func(self, *args, **kwargs)
    #     return wrapper

    def get_access_token(self):
        return self.main_window.profile_manager.access_token

    def init_ui(self):
        loadUi('data\\ui_files\\profile_screen.ui', self)

        self.main_screen_btn.clicked.connect(self.switch_to_main_screen)
        self.logout_btn.clicked.connect(self.logout)

    @token_required
    def load_profile_data(self):
        print('>>>>|', access_token)
        response = requests.get(
            f'http://{IP_ADDRESS}:{PORT}/profile', headers={'Authorization': f'Bearer {self.access_token}'})

        if response.status_code == 200:
            data = response.json()
            self.user_id_label.setText(str(data['id']))
            self.username_label.setText(data['username'])
            self.email_label.setText(data['email'])
        else:
            print("Ошибка при загрузке данных профиля:", response.status_code)

    # def refresh_access_token(self):
    #     response = requests.post(
    #         f'http://{IP_ADDRESS}:{PORT}/refresh-token', json={'refresh_token': self.refresh_token})

    #     if response.status_code == 200:
    #         try:
    #             json_response = response.json()
    #             self.access_token = json_response.get('access_token')
    #             access_token = json_response.get('access_token')
    #             with open('tokens.txt', 'w') as f:
    #                 f.write(self.access_token)
    #                 f.write('\n')
    #                 f.write(self.refresh_token)
    #         except ValueError:
    #             print("Ошибка декодирования JSON: пустой или некорректный ответ")
    #     else:
    #         try:
    #             print(response.json().get('message'))
    #         except ValueError:
    #             print("Ошибка декодирования JSON: пустой или некорректный ответ")
    #         print("Некорректный ответ от сервера или ошибка соединения")

    # def is_access_token_expiring_soon(self):
    #     response = requests.post(
    #         f'http://{IP_ADDRESS}:{PORT}/access-token-expiration',
    #         json={'access_token': self.access_token})

    #     if response.status_code == 200 and response.content:
    #         try:
    #             return response.json().get('is_valid')
    #         except ValueError:
    #             print("Ошибка декодирования JSON")
    #             return None
    #     else:
    #         print(response.json().get('message'))
    #         print("Некорректный ответ от сервера или ошибка соединения")
    #         return None

    def logout(self):
        self.access_token = ''
        self.refresh_token = ''
        with open('tokens.txt', 'w') as f:
            f.write('')
        self.switch_to_main_screen()

    def switch_to_main_screen(self):
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.main_window)
