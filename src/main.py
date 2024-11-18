import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QInputDialog, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt6.uic import loadUi
from config import *
import requests
from random import randint


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('ui_files\\main_screen.ui', self)

        # Чтение токенов
        try:
            with open('tokens.txt', 'r') as f:
                data = f.readlines()
                self.access_token = data[0].strip()
                self.refresh_token = data[1].strip()
        except Exception as e1:
            self.access_token = ''
            self.refresh_token = ''

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.main_screen = loadUi(
            'C:\\Users\\Redmi\\Documents\\DnD-Helper\\ui_files\\main_screen.ui')
        self.default_screen = loadUi(
            'C:\\Users\\Redmi\\Documents\\DnD-Helper\\ui_files\\default_screen.ui')
        self.login_screen = loadUi(
            'C:\\Users\\Redmi\\Documents\\DnD-Helper\\ui_files\\login_screen.ui')
        self.registration_screen = loadUi(
            'C:\\Users\\Redmi\\Documents\\DnD-Helper\\ui_files\\registration_screen.ui')
        self.profile_screen = loadUi(
            'C:\\Users\\Redmi\\Documents\\DnD-Helper\\ui_files\\profile_screen.ui')
        self.questionnaire_screen = loadUi(
            'C:\\Users\\Redmi\\Documents\\DnD-Helper\\ui_files\\questionnaire_screen.ui')
        self.create_questionnaire_screen = loadUi(
            'C:\\Users\\Redmi\\Documents\\DnD-Helper\\ui_files\\create_questionnaire_screen.ui')
        self.questionnaire_info_screen = loadUi(
            'C:\\Users\\Redmi\\Documents\\DnD-Helper\\ui_files\\questionnaire_info_screen.ui')
        self.questionnaire_edit_screen = loadUi(
            'C:\\Users\\Redmi\\Documents\\DnD-Helper\\ui_files\\questionnaire_edit_screen.ui')

        # Добавляем интерфейсы в QStackedWidget
        self.stacked_widget.addWidget(self.main_screen)
        self.stacked_widget.addWidget(self.default_screen)
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.registration_screen)
        self.stacked_widget.addWidget(self.profile_screen)
        self.stacked_widget.addWidget(self.questionnaire_screen)
        self.stacked_widget.addWidget(self.create_questionnaire_screen)
        self.stacked_widget.addWidget(self.questionnaire_info_screen)
        self.stacked_widget.addWidget(self.questionnaire_edit_screen)

        # Подключение кнопок main screen
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

        self.questionnaire_screen.to_main_btn.clicked.connect(
            self.switch_to_main_screen)
        self.questionnaire_screen.create_questionnaire_btn.clicked.connect(
            self.switch_to_create_questionnaire_screen)

        self.create_questionnaire_screen.back_btn.clicked.connect(
            self.switch_to_questionnaire_screen)
        self.create_questionnaire_screen.create_btn.clicked.connect(
            self.create_questionnaire)

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
        self.main_screen.throw_dice_btn.clicked.connect(self.throw_dice)

        self.profile_screen.main_screen_btn.clicked.connect(
            self.switch_to_main_screen)
        self.profile_screen.logout_btn.clicked.connect(
            self.logout)
        self.profile_screen.add_friend_btn.clicked.connect(
            self.add_friend)

        self.questionnaire_info_screen.back_btn.clicked.connect(
            self.switch_to_questionnaire_screen)

        self.questionnaire_edit_screen.back_btn.clicked.connect(
            self.switch_to_questionnaire_screen)

    def switch_to_main_screen(self):
        self.stacked_widget.setCurrentWidget(self.main_screen)

    def switch_to_create_questionnaire_screen(self):
        self.stacked_widget.setCurrentWidget(self.create_questionnaire_screen)

    def switch_to_groups_screen(self):
        self.stacked_widget.setCurrentWidget(self.default_screen)

    def switch_to_friends_screen(self):
        self.stacked_widget.setCurrentWidget(self.default_screen)

    def switch_to_account_screen(self):
        self.stacked_widget.setCurrentWidget(self.default_screen)

    def switch_to_registration_screen(self):
        self.registration_screen.reg_res.clear()
        self.registration_screen.email_le.clear()
        self.registration_screen.password_le.clear()
        self.registration_screen.username_le.clear()
        self.stacked_widget.setCurrentWidget(self.registration_screen)

    def switch_to_login_screen(self):
        self.login_screen.login_res.clear()
        self.login_screen.email_le.clear()
        self.login_screen.password_le.clear()
        self.stacked_widget.setCurrentWidget(self.login_screen)

    @staticmethod
    def token_required(func):
        def wrapper(self, *args, **kwargs):
            # Проверяем, истекает ли токен
            if not self.is_access_token_expiring_soon():
                print("Токен истекает, обновляем...")
                self.refresh_access_token()
            # Выполняем основную функцию
            return func(self, **kwargs)
        return wrapper

    def throw_dice(self):
        dices = ['D2', 'D4', 'D6', 'D8', 'D10', 'D12', 'D20']
        dice, ok = QInputDialog.getItem(
            self, 'Dices', 'Select dice:', dices, 0, False)
        if ok:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Question)

            msg.setText(f"{randint(1, int(dice.lstrip('D')))}")
            msg.setWindowTitle("Throwing dice")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

    @token_required
    def switch_to_questionnaire_screen(self):
        self.stacked_widget.setCurrentWidget(self.questionnaire_screen)
        response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/get_questionnaires', json={'access_token': self.access_token})
        if response.status_code == 200:
            self.buttons = []
            self.questionnaires = response.json().get('questionnaires')  # DEMO
            questionnaires = self.questionnaires

            button_widget = QWidget()
            button_layout = QVBoxLayout(button_widget)
            scroll_area = self.questionnaire_screen.scroll_area

            button_layout.setSpacing(10)

            for i in questionnaires:
                button = QPushButton(self.questionnaire_screen)
                button.setText(i['character_name'])
                self.buttons.append(button)
                button.setFixedSize(400, 50)
                button.clicked.connect(
                    self.switch_to_questionnaire_info_screen)
                button_layout.addWidget(button)

            button_widget.setLayout(button_layout)
            scroll_area.setWidget(button_widget)

            self.questionnaire_screen.layout().addWidget(scroll_area)
        else:
            print("Ошибка загрузки анкет:", response.status_code, response.text)

    def switch_to_questionnaire_info_screen(self):
        sender = self.sender()
        questionnaire = self.questionnaires[self.buttons.index(sender)]  # DEMO
        self.stacked_widget.setCurrentWidget(self.questionnaire_info_screen)
        screen = self.questionnaire_info_screen
        screen.name_label.setText(questionnaire['character_name'])
        screen.class_label.setText(questionnaire['class_name'])
        screen.species_label.setText(questionnaire['species'])
        screen.background_label.setText(questionnaire['background'])
        screen.world_view_label.setText(questionnaire['worldview'])
        screen.exp_label.setText(str(questionnaire['experience']))
        screen.level_label.setText(str(questionnaire['level']))

        try:
            screen.del_btn.clicked.disconnect()  # Очищаем предыдущие обработчики
        except TypeError:
            pass  # Игнорируем ошибку, если обработчик не был подключен

        # Подключаем новый обработчик
        screen.del_btn.clicked.connect(
            # Передаем правильный id
            lambda: self.del_questionnaire(questionnaire['id']))
        # self.questionnaire_info_screen.del_btn.clicked.connect(
        # lambda: self.del_questionnaire(questionnaire['id']))
        self.questionnaire_info_screen.edit_btn.clicked.connect(lambda:
                                                                self.switch_to_edit_questionnaire_screen(questionnaire))

    def del_questionnaire(self, id):
        response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/del_questionnaire', json={'id': id})
        if response.status_code == 200:
            print(response.json().get('message'))
            self.switch_to_questionnaire_screen()
        else:
            print(response.json().get('message'))

    def switch_to_edit_questionnaire_screen(self, questionnaire):
        self.stacked_widget.setCurrentWidget(self.questionnaire_edit_screen)
        screen = self.questionnaire_edit_screen
        screen.name_input.setText(questionnaire['character_name'])
        screen.class_input.setText(questionnaire['class_name'])
        screen.species_input.setText(questionnaire['species'])
        screen.background_input.setText(questionnaire['background'])
        screen.worldview_input.setText(questionnaire['worldview'])
        screen.exp_input.setValue(questionnaire['experience'])
        screen.level_input.setValue(questionnaire['level'])
        # print('>>', questionnaire['id'])
        screen.save_btn.blockSignals(True)

        try:
            screen.save_btn.clicked.disconnect()
        except TypeError:
            pass

        # Подключаем новый обработчик
        screen.save_btn.clicked.connect(
            lambda: self.edit_questionnaire(questionnaire['id']))

        # Разблокируем сигналы
        screen.save_btn.blockSignals(False)
        # screen.save_btn.clicked.disconnect()
        # screen.save_btn.clicked.connect(
        #     lambda: self.edit_questionnaire(questionnaire['id']))

    def edit_questionnaire(self, id):
        screen = self.questionnaire_edit_screen
        print(id)
        response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/edit_questionnaire', json={'id': id,
                                                                    'name': screen.name_input.text(),
                                                                    'class_name': screen.class_input.text(),
                                                                    'species': screen.species_input.text(),
                                                                    'background': screen.background_input.text(),
                                                                    'worldview': screen.worldview_input.text(),
                                                                    'experience': screen.exp_input.value(),
                                                                    'level': screen.level_input.value()})
        if response.status_code == 200:
            print('Анкета была отредактирована')
        else:
            # print("Хуета вышла")
            print(response.json().get('message'))

    def register(self):
        email = self.registration_screen.email_le.text()
        password = self.registration_screen.password_le.text()
        username = self.registration_screen.username_le.text()

        if email != '' and password != '':
            response = requests.post(
                f'http://{IP_ADDRESS}:{PORT}/registration', json={'email': email, 'password': password, 'username': username})

            if response.status_code == 200:
                self.registration_screen.reg_res.setText(
                    'registration successful')
                print('registration successful')
            else:
                self.registration_screen.reg_res.setText('registration failed')
                print('registration failed')
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
            self.access_token = response.json().get('access_token')
            self.refresh_token = response.json().get('refresh_token')

            with open('tokens.txt', 'w') as f:
                f.write(self.access_token)
                f.write('\n')
                f.write(self.refresh_token)
            print('login successful')
        else:
            self.login_screen.login_res.setText('login failed')
            # print("Login failed: ", response.json().get('message'))

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
    def profile_data(self):
        if self.access_token != '':
            if hasattr(self, 'access_token'):
                response = requests.get(
                    f'http://{IP_ADDRESS}:{PORT}/profile', headers={'Authorization': f'Bearer {self.access_token}'})
                data = response.json()
                print(data)
                print(self.is_access_token_expiring_soon())
                self.stacked_widget.setCurrentWidget(self.profile_screen)
                self.profile_screen.user_id_label.setText(str(data['id']))
                self.profile_screen.username_label.setText(data['username'])
                self.profile_screen.email_label.setText(data['email'])
            else:
                self.refresh_access_token()
                if hasattr(self, 'access_token'):
                    response = requests.get(
                        f'http://{IP_ADDRESS}:{PORT}/profile', headers={'Authorization': f'Bearer {self.access_token}'})
                    data = response.json()
                    print(data)
                    self.stacked_widget.setCurrentWidget(self.profile_screen)
                    self.profile_screen.user_id_label.setText(str(data['id']))
                    self.profile_screen.username_label.setText(
                        data['username'])
                    self.profile_screen.email_label.setText(data['email'])
                else:
                    print('token not found')
                    self.switch_to_login_screen()
        else:
            self.switch_to_login_screen()

    def refresh_access_token(self):
        response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/refresh-token', json={'refresh_token': self.refresh_token})

        if response.status_code == 200:
            try:
                json_response = response.json()
                self.access_token = json_response.get('access_token')
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

        # Проверяем, что ответ не пустой и имеет статус 200
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

    def logout(self):
        self.access_token = ''
        self.refresh_token = ''
        with open('tokens.txt', 'w') as f:
            f.write('')
        self.switch_to_main_screen()

    @token_required
    def create_questionnaire(self):
        class_name = self.create_questionnaire_screen.class_input.text()
        species = self.create_questionnaire_screen.species_input.text()
        background = self.create_questionnaire_screen.background_input.text()
        worldview = self.create_questionnaire_screen.worldview_input.text()
        experience = self.create_questionnaire_screen.exp_input.value()
        level = self.create_questionnaire_screen.level_input.value()
        character_name = self.create_questionnaire_screen.name_input.text()
        response = requests.post(f'http://{IP_ADDRESS}:{PORT}/create_new_questionnaire', json={
                                 'access_token': self.access_token, 'class_name': class_name, 'species': species, 'background': background,
                                 'worldview': worldview, 'experience': experience, 'level': level, 'character_name': character_name})

        if response.status_code == 200:
            print("Анкета создана")
        else:
            # print(response.json().get('message'))
            print('ОШИБКА')

    def delete_questionnaire(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
