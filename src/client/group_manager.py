from PyQt6.QtWidgets import QMainWindow, QDialog, QDateEdit, QVBoxLayout, QWidget, QPushButton, QInputDialog, QMessageBox, QLabel
from PyQt6.uic import loadUi
from PyQt6.QtCore import QDate
import requests
from my_config import *


class DateInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выберите дату")

        self.layout = QVBoxLayout(self)

        self.date_edit = QDateEdit(self)
        # Включаем всплывающее окно календаря
        self.date_edit.setCalendarPopup(True)
        self.layout.addWidget(self.date_edit)

        self.ok_button = QPushButton("ОК", self)
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)

    def get_date(self):
        return self.date_edit.date().toString("dd-MM-yyyy")


class GroupManager(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.access_token = access_token
        self.refresh_token = refresh_token
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
            try:
                if not self.is_access_token_expiring_soon():
                    print("Токен истекает, обновляем...")
                    self.refresh_access_token()
                if self.access_token == '':
                    print("Токен недействителен, перенаправляем на экран входа...")
                    self.main_window.switch_to_login_screen()
                    return
                return func(self, **kwargs)
            except Exception as e:
                print(str(e))
                self.switch_to_main_screen()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText(f"Нет подключения к интернету")
                msg.setWindowTitle("Error")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
        return wrapper

    def refresh_access_token(self):
        response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/refresh-token', json={'refresh_token': self.refresh_token})

        if response.status_code == 200:
            try:
                json_response = response.json()
                self.access_token = json_response.get('access_token')
                access_token = json_response.get('access_token')
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
        loadUi('data/ui_files/group_list_screen.ui', self)

        self.group_screen = self.main_window.group_screen
        self.notebook_screen = self.main_window.notebook_screen

        self.create_group_btn.clicked.connect(self.create_group)
        self.back_btn.clicked.connect(self.switch_to_main_screen)
        self.join_group_btn.clicked.connect(self.join_group)
        self.notebook_screen.back_btn.clicked.connect(
            self.switch_to_group_screen_with_save)
        self.notebook_screen.save_btn.triggered.connect(
            self.save_plot)
        self.group_screen.back_btn.clicked.connect(
            self.switch_to_group_list_screen)
        self.group_screen.plot_btn.clicked.connect(self.switch_to_notebook)
        self.group_screen.set_game_date_btn.clicked.connect(self.set_game_date)
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

    @token_required
    def switch_to_group_screen(self):
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.group_screen)
        self.load_group_interface()
        # self.main_window.groups_screen.back_btn.clicked.connect(
        #     self.switch_to_group_list_screen)

    def switch_to_group_list_screen(self):
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.group_manager)
        self.load_groups()

    @token_required
    def load_group_interface(self):
        if self.sender().property('group_id'):
            self.group_id = self.sender().property('group_id')
            self.is_dm = self.sender().property('dm')
        if self.is_dm:
            self.group_screen.dm_name.setText('ВЫ')
        else:
            response = requests.post(
                f'http://{IP_ADDRESS}:{PORT}/get_owner_username', json={'group_id': self.group_id})
            if response.status_code == 200:
                self.group_screen.dm_name.setText(
                    response.json().get('username'))
                print(response.json().get('date'))

        self.group_screen.group_id_lb.setText(str(self.group_id))

        response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/get_group_info', json={'group_id': self.group_id})

        if response.status_code == 200:
            members = response.json().get('members')
            game_date = response.json().get('game_date')

            date = QDate.fromString(game_date, 'yyyy-MM-dd')
            self.group_screen.games_calendar.setSelectedDate(date)

            button_widget = QWidget()
            button_layout = QVBoxLayout(button_widget)
            scroll_area = self.group_screen.scroll_area

            button_layout.setSpacing(10)

            for i in members:
                member = QLabel(self.group_screen)
                member.setText(i['username'])
                member.setFixedSize(400, 50)
                button_layout.addWidget(member)

            button_widget.setLayout(button_layout)
            scroll_area.setWidget(button_widget)

            if not self.is_dm:
                self.group_screen.set_game_date_btn.hide()
            else:
                self.group_screen.set_game_date_btn.show()
        else:
            print("ОШИБКА")

    @token_required
    def switch_to_notebook(self):
        self.main_window.stacked_widget.setCurrentWidget(self.notebook_screen)

        response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/get_plot', json={'group_id': self.group_id})

        if response.status_code == 200:
            self.notebook_screen.plot_editor.setPlainText(
                response.json().get('plot'))

        if self.is_dm:
            self.notebook_screen.plot_editor.setReadOnly(False)
        else:
            self.notebook_screen.menubar.setVisible(False)
            self.notebook_screen.plot_editor.setReadOnly(True)

    def save_plot(self):
        response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/edit_plot', json={'group_id': self.group_id, 'plot': self.main_window.notebook_screen.plot_editor.toPlainText()})
        if response.status_code == 200:
            print('plot was edited')

    @token_required
    def switch_to_group_screen_with_save(self):
        self.save_plot()
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.group_screen)
        self.load_group_interface()
        self.main_window.group_screen.back_btn.clicked.connect(
            self.switch_to_group_list_screen)

    def set_game_date(self):
        dialog = DateInputDialog(self)
        if dialog.exec():
            selected_date = dialog.get_date()
            response = requests.post(
                f'http://{IP_ADDRESS}:{PORT}/set_game_date', json={'group_id': self.group_id, 'date': selected_date})

    def switch_to_main_screen(self):
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.main_window)
