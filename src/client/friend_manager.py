from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QInputDialog
from PyQt6.uic import loadUi
import requests
from config import *
from my_token import token_required


class FriendManager(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
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
    #         return func(self, **kwargs)
    #     return wrapper

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

    def init_ui(self):
        loadUi('data\\ui_files\\frends_list_screen.ui')
        self.setLayout(QVBoxLayout())

    @token_required
    def add_friend(self):
        id, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter user ID:')
        if ok:
            print(id)
            response = requests.post(
                f'http://{IP_ADDRESS}:{PORT}/add-friend', json={'user_token': self.access_token, 'friend_id': f'{id}'})
            if response.status_code == 200:
                print(response.json().get('message'))
            else:
                print(response.json().get('message'))

    @token_required
    def load_friends_data(self):
        response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/get_friends', json={'access_token': self.access_token})
        if response.status_code == 200:
            self.buttons = []
            self.friends = response.json().get('friends')
            friends = self.friends

            button_widget = QWidget()
            button_layout = QVBoxLayout(button_widget)
            scroll_area = self.main_window.questionnaire_screen.scroll_area

            button_layout.setSpacing(10)

            for i in friends:
                button = QPushButton(self)
                button.setText(i['user_name'])
                self.buttons.append(button)
                button.setFixedSize(400, 50)
                button_layout.addWidget(button)

            button_widget.setLayout(button_layout)
            scroll_area.setWidget(button_widget)

            self.layout().addWidget(scroll_area)
        else:
            print("Ошибка загрузки анкет:", response.status_code, response.text)
