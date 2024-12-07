from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QMessageBox
import requests
from my_config import *
from PyQt6.uic import loadUi
# from my_token import token_required


class QuestionnaireManager(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.init_ui()

    # декоратор для проверки актуальности access токена перед его использованием
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
                self.switch_to_main_screen()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText(f"Нет подключения к интернету")
                msg.setWindowTitle("Error")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
        return wrapper

    # Функция обновления access токена
    def refresh_access_token(self):
        response = requests.post(
            f"http://{IP_ADDRESS}:{PORT}/refresh-token', json={'refresh_token': self.refresh_token}")

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

    # Функция проверки того, насколько скоро access токен прекратит работу
    def is_access_token_expiring_soon(self):
        response = requests.post(
            f"http://{IP_ADDRESS}:{PORT}/access-token-expiration',
            json={'access_token': self.access_token}")

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
        loadUi('data/ui_files/questionnaire_screen.ui', self)

        self.create_questionnaire_screen = self.main_window.create_questionnaire_screen

        # Привязка функционала кнопкам
        self.to_main_btn.clicked.connect(self.switch_to_main_screen)
        self.create_questionnaire_btn.clicked.connect(
            self.switch_to_create_questionnaire_screen)
        self.throw_dice_btn.clicked.connect(self.main_window.throw_dice)
        self.account_btn.clicked.connect(
            self.main_window.switch_to_profile_screen)
        self.main_window.questionnaire_info_screen.throw_dice_btn.clicked.connect(
            self.main_window.throw_dice)
        self.main_window.questionnaire_info_screen.account_btn.clicked.connect(
            self.main_window.switch_to_profile_screen)
        self.main_window.questionnaire_edit_screen.throw_dice_btn.clicked.connect(
            self.main_window.throw_dice)
        self.main_window.questionnaire_edit_screen.account_btn.clicked.connect(
            self.main_window.switch_to_profile_screen)

    # Переход к списку анкет
    def to_questionnaire_list(self):
        self.main_window.switch_to_questionnaire_screen()

    # Подгрузка всех анкет из профиля
    @token_required
    def load_questionnaire_data(self):
        response = requests.post(
            f"http://{IP_ADDRESS}:{PORT}/get_questionnaires', json={'access_token': self.access_token}")
        if response.status_code == 200:
            self.buttons = []
            self.questionnaires = response.json().get('questionnaires')
            questionnaires = self.questionnaires

            button_widget = QWidget()
            button_layout = QVBoxLayout(button_widget)
            scroll_area = self.main_window.questionnaire_screen.scroll_area

            button_layout.setSpacing(10)

            for i in questionnaires:
                button = QPushButton(self)
                button.setText(i['character_name'])
                self.buttons.append(button)
                button.setFixedSize(400, 50)
                button.clicked.connect(
                    self.switch_to_questionnaire_info_screen)
                button_layout.addWidget(button)

            button_widget.setLayout(button_layout)
            scroll_area.setWidget(button_widget)

            self.layout().addWidget(scroll_area)
        else:
            print("Ошибка загрузки анкет:", response.status_code, response.text)

    # Переход на экран анкеты
    @token_required
    def switch_to_questionnaire_info_screen(self):
        sender = self.sender()
        screen = self.main_window.questionnaire_info_screen
        questionnaire = self.questionnaires[self.buttons.index(sender)]
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.questionnaire_info_screen)
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
            lambda: self.del_questionnaire(questionnaire['id']))
        screen.back_btn.clicked.connect(
            self.to_questionnaire_list)
        screen.edit_btn.clicked.connect(lambda:
                                        self.switch_to_edit_questionnaire_screen(questionnaire))

    # Переход на главный экран
    def switch_to_main_screen(self):
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.main_window)

    # переход на страницу редактирования анкеты
    def switch_to_edit_questionnaire_screen(self, questionnaire):
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.questionnaire_edit_screen)
        screen = self.main_window.questionnaire_edit_screen
        screen.name_input.setText(questionnaire['character_name'])
        screen.class_input.setText(questionnaire['class_name'])
        screen.species_input.setText(questionnaire['species'])
        screen.background_input.setText(questionnaire['background'])
        screen.worldview_input.setText(questionnaire['worldview'])
        screen.exp_input.setValue(questionnaire['experience'])
        screen.level_input.setValue(questionnaire['level'])
        # print('>>', questionnaire['id'])
        screen.save_btn.blockSignals(True)

        screen.back_btn.clicked.connect(self.to_questionnaire_list)

        try:
            screen.save_btn.clicked.disconnect()
        except TypeError:
            pass

        # Подключаем новый обработчик
        screen.save_btn.clicked.connect(
            lambda: self.edit_questionnaire(questionnaire['id']))

        # Разблокируем сигналы
        screen.save_btn.blockSignals(False)

    # Переход на страницу создания анкеты
    def switch_to_create_questionnaire_screen(self):
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.create_questionnaire_screen)
        self.main_window.create_questionnaire_screen.create_btn.clicked.connect(
            self.create_questionnaire)
        self.main_window.create_questionnaire_screen.back_btn.clicked.connect(
            self.to_questionnaire_list)

    # Редактирование анкеты
    def edit_questionnaire(self, id):
        screen = self.main_window.questionnaire_edit_screen
        print(id)
        response = requests.post(
            f"http://{IP_ADDRESS}:{PORT}/edit_questionnaire", json={'id': id,
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
            print(response.json().get('message'))

    # функция для создания анкеты
    @token_required
    def create_questionnaire(self):
        screen = self.main_window.create_questionnaire_screen
        class_name = screen.class_input.text()
        species = screen.species_input.text()
        background = screen.background_input.text()
        worldview = screen.worldview_input.text()
        experience = screen.exp_input.value()
        level = screen.level_input.value()
        character_name = screen.name_input.text()
        response = requests.post(f"http://{IP_ADDRESS}:{PORT}/create_new_questionnaire", json={
                                 'access_token': self.access_token, 'class_name': class_name, 'species': species, 'background': background,
                                 'worldview': worldview, 'experience': experience, 'level': level, 'character_name': character_name})

        if response.status_code == 200:
            print("Анкета создана")
            self.main_window.switch_to_questionnaire_screen()
        else:
            # print(response.json().get('message'))
            print('ОШИБКА')

    # Функция для удаления анкеты
    def del_questionnaire(self, id):
        response = requests.post(
            f"http://{IP_ADDRESS}:{PORT}/del_questionnaire", json={'id': id})
        if response.status_code == 200:
            print(response.json().get('message'))
            self.to_questionnaire_list()
        else:
            print(response.json().get('message'))
