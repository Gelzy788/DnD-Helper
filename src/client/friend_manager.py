from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QInputDialog, QMessageBox
from PyQt6.uic import loadUi
import requests
from my_config import *
from my_token import token_required


class FriendManager(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    @staticmethod
    def token_required(func):
        def wrapper(self, *args, **kwargs):
            try:
                with open('tokens.txt', 'r') as f:
                    data = f.readlines()
                    self.access_token = data[0].strip()
                    self.refresh_token = data[1].strip()
            except Exception as e1:
                print('ОШИБКА')
                self.main_window.stacked_widget.setCurrentWidget(
                    self.main_window.main_window)
            if not self.is_access_token_expiring_soon():
                print("Токен истекает, обновляем...")
                self.refresh_access_token()
            if self.access_token == '':
                print("Токен недействителен, перенаправляем на экран входа...")
                self.main_window.stacked_widget.setCurrentWidget(
                    self.main_window.login_manager)
                return
            return func(self, **kwargs)
        return wrapper

    def refresh_access_token(self):
        response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/refresh-token', json={'refresh_token': self.refresh_token})

        if response.status_code == 200:
            try:
                json_response = response.json()
                self.access_token = json_response.get('access_token')
                self.access_token = json_response.get(
                    'access_token')  # ДОБАВИЛ .self!
                with open('tokens.txt', 'w') as f:
                    f.write(self.access_token)
                    f.write('\n')
                    f.write(self.refresh_token)
            except ValueError:
                print("Ошибка декодирования JSON: пустой или некорректный ответ")
        else:
            try:
                print(response.json().get('message'))
            except ValueError:
                print("Ошибка декодирования JSON: пустой или некорректный ответ")
            print("Некорректный ответ от сервера или ошибка соединения")

    def is_access_token_expiring_soon(self):
        response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/access-token-expiration',
            json={'access_token': self.access_token})

        if response.status_code == 200 and response.content:
            try:
                return response.json().get('is_valid')
            except ValueError:
                print("Ошибка декодирования JSON")
                return None
        else:
            print(response.json().get('message'))
            print("Некорректный ответ от сервера или ошибка соединения")
            return None

    def init_ui(self):
        loadUi('data\\ui_files\\frends_list_screen.ui', self)

        # self.friend_requests_screen = loadUi('data/ui_files/friend_requests_screen.ui')

        self.add_friend_btn.clicked.connect(self.add_friend)
        self.back_btn.clicked.connect(self.switch_to_main_menu)
        self.friend_requests_btn.clicked.connect(
            self.switch_to_friend_requests_screen)

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
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Information)

                msg.setText(f'{response.json().get('message')}')
                msg.setWindowTitle("Error")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()

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
            scroll_area = self.scroll_area

            button_layout.setSpacing(10)

            for i in friends:
                if i['status'] == 1:
                    button = QPushButton(self)
                    button.setText(i['user_name'])
                    self.buttons.append(button)
                    button.setFixedSize(400, 50)
                    button.clicked.connect(
                        self.delete_friend)
                    button_layout.addWidget(button)

            button_widget.setLayout(button_layout)
            scroll_area.setWidget(button_widget)

            self.layout().addWidget(scroll_area)
        else:
            print("Ошибка загрузки друзей:",
                  response.status_code, response.text)

    def switch_to_friend_requests_screen(self):
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.friend_requests_screen)
        self.main_window.friend_requests_screen.back_btn.clicked.connect(
            self.main_window.switch_to_friends_list_screen)
        self.load_friend_requests()

    @token_required
    def load_friend_requests(self):
        response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/get_friends', json={'access_token': self.access_token})
        if response.status_code == 200:
            self.buttons = []
            self.friends = response.json().get('friends')
            friends = self.friends
            id = response = requests.get(
                f'http://{IP_ADDRESS}:{PORT}/profile', headers={'Authorization': f'Bearer {self.access_token}'}).json()['id']

            button_widget = QWidget()
            button_layout = QVBoxLayout(button_widget)
            scroll_area = self.main_window.friend_requests_screen.scroll_area

            button_layout.setSpacing(10)

            for i in friends:
                if i['status'] == 0 and i['user_id'] != id:
                    # if i['status'] == 0:
                    button = QPushButton(self)
                    button.setText(i['user_name'])
                    self.buttons.append(button)
                    button.setFixedSize(400, 50)
                    button.clicked.connect(
                        self.accept_friend_request)
                    button_layout.addWidget(button)

            button_widget.setLayout(button_layout)
            scroll_area.setWidget(button_widget)

            self.main_window.friend_requests_screen.layout().addWidget(scroll_area)
        else:
            print("Ошибка загрузки друзей:",
                  response.status_code, response.text)

    @token_required
    def accept_friend_request(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)

        msg.setText(f'Вы хотите добавить в друзья {self.sender().text()}?')
        msg.setWindowTitle("Добавление в друзья")
        msg.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        returnValue = msg.exec()
        if returnValue == QMessageBox.StandardButton.Ok:
            friends_couple = self.friends[self.buttons.index(self.sender())]
            response = requests.post(
                f'http://{IP_ADDRESS}:{PORT}/update_friendship_status', json={'user_id': friends_couple['user_id'], 'friend_id': friends_couple['friend_id']})
            if response.status_code == 200:
                print('Друг добавлен')
                self.load_friend_requests
            else:
                print(response.json().get('message'))
        else:
            # Может произойти баг и все друзья удалятся(или не все. Я не знаю)
            friends_couple = self.friends[self.buttons.index(self.sender())]
            response = requests.post(
                f'http://{IP_ADDRESS}:{PORT}/delete_friend_request', json={'user_id': friends_couple['user_id'], 'friend_id': friends_couple['friend_id']})
            if response.status_code == 200:
                print('Приглашение отклонено')
                self.load_friend_requests
            else:
                print(response.json.get('message'))

    def delete_friend(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)

        msg.setText(f'Вы хотите удалить пользователя {
                    self.sender().text()} из друзей?')
        msg.setWindowTitle("Добавление в друзья")
        msg.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        returnValue = msg.exec()
        if returnValue == QMessageBox.StandardButton.Ok:
            friends_couple = self.friends[self.buttons.index(self.sender())]
            response = requests.post(
                f'http://{IP_ADDRESS}:{PORT}/update_friendship_status', json={'user_id': friends_couple['user_id'], 'friend_id': friends_couple['friend_id']})
            if response.status_code == 200:
                print('Друг удален')
                self.load_friends_data
            else:
                print(response.json().get('message'))

    def switch_to_main_menu(self):
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.main_window)
