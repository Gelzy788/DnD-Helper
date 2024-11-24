from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QInputDialog, QMessageBox
from random import randint
from friend_manager import FriendManager
from questionnaire_manager import QuestionnaireManager
from group_manager import GroupManager
from login_manager import LoginManager
from register_manager import RegisterManager
from profile_manager import ProfileManager
from PyQt6.uic import loadUi
from my_config import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('data\\ui_files\\main_screen.ui', self)

        # with open("tokens.txt", 'r') as f:
        #         print('MAIN WONDOW:')
        #         print(access_token, '>>', refresh_token)
        #         print(f.readlines())
        #         print(';;;')

        # try:
        #     with open('tokens.txt', 'r') as f:
        #         data = f.readlines()
        #         access_token = data[0].strip()
        #         refresh_token = data[1].strip()
        # except Exception as e1:
        #     access_token = ''
        #     refresh_token = ''

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Инициализация менеджеров
        self.profile_manager = ProfileManager(
            self, access_token, refresh_token)
        self.login_manager = LoginManager(self)
        self.register_manager = RegisterManager(self)
        self.friend_manager = FriendManager(self)
        self.questionnaire_manager = QuestionnaireManager(self)
        self.group_manager = GroupManager(self)
        self.questionnaire_screen = loadUi(
            'data\\ui_files\\questionnaire_screen.ui')
        self.create_questionnaire_screen = loadUi(
            'data\\ui_files\\create_questionnaire_screen.ui')
        self.questionnaire_info_screen = loadUi(
            'data\\ui_files\\questionnaire_info_screen.ui')
        self.questionnaire_edit_screen = loadUi(
            'data\\ui_files\\questionnaire_edit_screen.ui')
        self.main_window = loadUi('data\\ui_files\\main_screen.ui')
        self.friend_requests_screen = loadUi('data/ui_files/friend_requests_screen.ui')

        # Добавление экранов в QStackedWidget
        self.stacked_widget.addWidget(self.profile_manager)
        self.stacked_widget.addWidget(self.login_manager)
        self.stacked_widget.addWidget(self.register_manager)
        self.stacked_widget.addWidget(self.friend_manager)
        self.stacked_widget.addWidget(self.questionnaire_manager)
        self.stacked_widget.addWidget(self.group_manager)
        self.stacked_widget.addWidget(self.main_window)
        self.stacked_widget.addWidget(self.questionnaire_screen)
        self.stacked_widget.addWidget(self.create_questionnaire_screen)
        self.stacked_widget.addWidget(self.questionnaire_info_screen)
        self.stacked_widget.addWidget(self.questionnaire_edit_screen)
        self.stacked_widget.addWidget(self.friend_requests_screen)

        # Установка начального экрана
        self.stacked_widget.setCurrentWidget(self.main_window)

        # Кнопки
        self.main_window.reg_btn.clicked.connect(
            self.switch_to_registration_screen)
        self.main_window.login_btn.clicked.connect(self.switch_to_login_screen)
        self.main_window.account_btn.clicked.connect(
            self.switch_to_profile_screen)
        self.main_window.questionnaires_btn.clicked.connect(
            self.switch_to_questionnaire_screen)
        self.main_window.throw_dice_btn.clicked.connect(self.throw_dice)
        self.main_window.friends_btn.clicked.connect(
            self.switch_to_friends_list_screen)

    def switch_to_registration_screen(self):
        self.stacked_widget.setCurrentWidget(self.register_manager)

    def switch_to_login_screen(self):
        self.stacked_widget.setCurrentWidget(self.login_manager)

    def switch_to_friends_list_screen(self):
        self.stacked_widget.setCurrentWidget(self.friend_manager)
        self.friend_manager.load_friends_data()

    def switch_to_profile_screen(self):
        # Загружаем данные профиля при переключении
        self.stacked_widget.setCurrentWidget(self.profile_manager)
        self.profile_manager.load_profile_data()

    def switch_to_questionnaire_screen(self):
        self.stacked_widget.setCurrentWidget(self.questionnaire_manager)
        self.questionnaire_manager.load_questionnaire_data()

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
