from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QInputDialog, QMessageBox, QLabel
from PyQt6.uic import loadUi
import requests
from my_config import *


class GroupManager(QMainWindow):
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
        loadUi('data\\ui_files\\group_list_screen.ui', self)

        self.create_group_btn.clicked.connect(self.create_group)
        self.back_btn.clicked.connect(self.switch_to_main_screen)
        self.join_group_btn.clicked.connect(self.join_group)
        # self.main_window.notebook_screen.plot_btn.clicked.connect(
        #     self.switch_to_notebook)

    @token_required
    def load_groups(self):
        response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/get_groups', json={'access_token': self.access_token})
        if response.status_code == 200:
            self.buttons = []
            self.owner_groups = response.json().get('user owner groups')
            self.participant_groups = response.json().get('user participant groups')
            # id = response = requests.get(
            #     f'http://{IP_ADDRESS}:{PORT}/profile', headers={'Authorization': f'Bearer {self.access_token}'}).json()['id']

            button_widget = QWidget()
            button_layout = QVBoxLayout(button_widget)
            scroll_area = self.scroll_area  # Может нужно поменять

            button_layout.setSpacing(10)

            # Вывод групп, которыми пользователь владеет
            for i in self.owner_groups:
                button = QPushButton(self)
                button.setText(f'👑 {i['name']}')
                self.buttons.append(button)
                button.setProperty('group_id', i['id'])
                button.setProperty('dm', True)
                button.setFixedSize(400, 50)
                button.clicked.connect(
                    self.switch_to_group_screen)
                button_layout.addWidget(button)

            # Вывод остальных групп
            for i in self.participant_groups:
                button = QPushButton(self)
                button.setText(f'{i['name']}')
                self.buttons.append(button)
                button.setProperty('group_id', i['group_id'])
                # print(f'{i['name']} - {i['group_id']}')
                button.setProperty('dm', False)
                button.setFixedSize(400, 50)
                button.clicked.connect(
                    self.switch_to_group_screen)
                button_layout.addWidget(button)

            button_widget.setLayout(button_layout)
            scroll_area.setWidget(button_widget)

            self.layout().addWidget(scroll_area)
        else:
            print("Ошибка загрузки друзей:",
                  response.status_code, response.text)

    @token_required
    def join_group(self):
        group_id, ok = QInputDialog.getInt(
            self, 'Новая группа', 'Введите название группы:', 0, 1, 10000, 1)

        if ok:
            response = requests.post(
                f'http://{IP_ADDRESS}:{PORT}/add_user_to_group', json={'access_token': self.access_token, 'group_id': group_id})
            if response.status_code == 200:
                msg = QMessageBox()
                msg.setText('Группа')
                msg.setWindowTitle("Вы присоединились к группе")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
                self.load_groups()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText(f'{response.json().get('message')}')
                msg.setWindowTitle("Ошибка подключения к группе")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()

    @token_required
    def create_group(self):
        name, ok = QInputDialog.getText(
            self, 'Новая группа', 'Введите название группы:')

        if ok and name.strip() != '':
            response = requests.post(
                f'http://{IP_ADDRESS}:{PORT}/create_group', json={'access_token': self.access_token, 'name': name})

            if response.status_code == 200:
                msg = QMessageBox()
                # msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText('Группа создана')
                msg.setWindowTitle("Группа создана")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()

                self.load_groups()

            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText(f'{response.json().get('message')}')
                msg.setWindowTitle("Ошибка создания группы")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()

        elif name.strip() == '':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText('Введите название группы!')
            msg.setWindowTitle("Введите название группы")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

    def switch_to_group_screen(self):
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.groups_screen)
        self.load_group_interface()
        self.main_window.groups_screen.back_btn.clicked.connect(
            self.main_window.switch_to_group_list_screen)

    def load_group_interface(self):
        screen = self.main_window.groups_screen
        group_id = self.sender().property('group_id')
        is_dm = self.sender().property('dm')
        if is_dm:
            screen.dm_name.setText('ВЫ')
        else:
            response = requests.post(
                f'http://{IP_ADDRESS}:{PORT}/get_owner_username', json={'group_id': group_id})
            if response.status_code == 200:
                screen.dm_name.setText(response.json().get('username'))

        screen.group_id_lb.setText(str(group_id))

        response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/get_group_members', json={'group_id': group_id})

        if response.status_code == 200:
            members = response.json().get('members')
            # print(members)

            button_widget = QWidget()
            button_layout = QVBoxLayout(button_widget)
            scroll_area = screen.scroll_area

            button_layout.setSpacing(10)

            for i in members:
                member = QLabel(screen)
                member.setText(i['username'])
                member.setFixedSize(400, 50)
                button_layout.addWidget(member)

            button_widget.setLayout(button_layout)
            scroll_area.setWidget(button_widget)
        else:
            print("ОШИБКА")
        screen.plot_btn.setProperty('id', group_id)
        screen.plot_btn.setProperty('is_dm', is_dm)
        screen.plot_btn.clicked.connect(self.switch_to_notebook)

    def switch_to_notebook(self):
        group_id = self.sender().property('id')
        screen = self.main_window.notebook_screen
        self.main_window.stacked_widget.setCurrentWidget(screen)

        response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/get_plot', json={'group_id': group_id})

        if response.status_code == 200:
            screen.plot_editor.setPlainText(response.json().get('plot'))

        if self.sender().property('is_dm'):
            screen.plot_editor.setReadOnly(False)
        else:
            screen.plot_editor.setReadOnly(True)

        screen.back_btn.setProperty('group_id', group_id)
        screen.back_btn.setProperty('dm', self.sender().property('is_dm'))
        screen.back_btn.clicked.connect(self.switch_to_group_screen)

# Бесполезный комментарий
    def switch_to_main_screen(self):
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.main_window)
