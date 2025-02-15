from PyQt6.QtWidgets import QMainWindow, QFileDialog, QInputDialog, QMessageBox
from PyQt6.uic import loadUi
from PyQt6.QtGui import QPixmap, QPainter, QRegion
import requests
from my_config import *
from random import randint
# from archive.my_token import token_required


class ProfileManager(QMainWindow):
    def __init__(self, main_window, access_token, refresh_token):
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
                return func(self, *args, **kwargs)
            except Exception as e:
                self.switch_to_main_screen()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText(f"Нет подключения к интернету")
                msg.setWindowTitle("Error")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
        return wrapper

    # Функция получения access токена
    def get_access_token(self):
        return self.main_window.profile_manager.access_token

    def init_ui(self):
        loadUi('data/ui_files/profile_screen.ui', self)

        self.edit_screen = self.main_window.edit_profile_screen

        # Кнопки
        self.main_screen_btn.clicked.connect(self.switch_to_main_screen)
        self.logout_btn.clicked.connect(self.logout)
        self.upload_image_btn.clicked.connect(self.load_image)
        self.edit_profile_btn.clicked.connect(self.switch_to_edit_profile)
        self.edit_screen.back_btn.clicked.connect(self.switch_back_with_save)
        self.edit_screen.throw_dice_btn.clicked.connect(self.throw_dice)

    # Функция подгрузки информации
    @token_required
    def load_profile_data(self):
        response = requests.get(
            f'http://{IP_ADDRESS}:{PORT}/profile', headers={'Authorization': f'Bearer {self.access_token}'})
        picture_response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/get_profile_picture',
            json={'access_token': self.access_token})

        if response.status_code == 200:
            data = response.json()
            self.user_id_label.setText(str(data['id']))
            self.username_label.setText(data['username'])
            self.email_label.setText(data['email'])
            self.telegram_label.setText(data['telegram'])
            self.vk_label.setText(data['vk'])

            with open("profile_image.jpeg", 'wb') as f:
                f.write(picture_response.content)

            # self.setLayout(self.hbox)
            profile_picture = QPixmap("profile_image.jpeg")
            self.image_label.setPixmap(profile_picture)
            self.image_label.setScaledContents(True)
        else:
            print("Ошибка при загрузке данных профиля:", response.status_code)

    # Функция обновления access токена

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

    # Функция проверки того, насколько скоро access токен прекратит работу
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

    # Выход из аккаунта
    def logout(self):
        self.access_token = ''
        self.refresh_token = ''
        with open('tokens.txt', 'w') as f:
            f.write('')
        self.switch_to_main_screen()

    # Переход на главный экран
    def switch_to_main_screen(self):
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.main_window)

    def load_image(self):
        # Открываем диалоговое окно для выбора файла
        options = QFileDialog(self).options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)

        if file_name:
            # Загружаем изображение и отображаем его
            self.image_path = file_name  # Сохраняем путь к изображению
            pixmap = QPixmap(file_name)
            self.image_label.setPixmap(pixmap)  # Масштабируем изображение
            self.send_image()

    def send_image(self):
        if self.image_path is None:
            QMessageBox.warning(
                self, "Ошибка", "Сначала выберите изображение для загрузки.")
            return

        # Замените на адрес вашего сервера
        url = f'http://{IP_ADDRESS}:{PORT}/upload-profile-image'
        # Открываем файл в бинарном режиме
        files = {'file': open(self.image_path, 'rb')}

        try:
            response = requests.post(
                url, data={'access_token': self.access_token}, files=files)
            if response.status_code == 200:
                QMessageBox.information(
                    self, "Успех", "Изображение успешно загружено на сервер.")
            else:
                QMessageBox.warning(
                    self, "Ошибка", f"Не удалось загрузить изображение. Код ошибки: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Произошла ошибка при отправке изображения: {str(e)}")
        finally:
            files['file'].close()  # Закрываем файл после отправки

    def switch_to_edit_profile(self):
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.edit_profile_screen)
        response = requests.get(
            f'http://{IP_ADDRESS}:{PORT}/profile', headers={'Authorization': f'Bearer {self.access_token}'})

        if response.status_code == 200:
            data = response.json()
            self.edit_screen.nickname_input.setText(data["username"])
            self.edit_screen.mail_input.setText(data["email"])
            self.edit_screen.telegram_input.setText(data["telegram"])
            self.edit_screen.vk_input.setText(data["vk"])
            self.edit_screen.description_editor.setText(data["description"])

    def switch_back_with_save(self):
        response = requests.post(
            f'http://{IP_ADDRESS}:{PORT}/edit-profile-info',
            json={'access_token': self.access_token, 'username': self.edit_screen.nickname_input.text(),
                  'email': self.edit_screen.mail_input.text(), 'telegram': self.edit_screen.telegram_input.text(),
                  'vk': self.edit_screen.vk_input.text(), 'description': self.edit_screen.description_editor.toPlainText()})
        if response.status_code == 200:
            print("Данный обновлены")
        self.main_window.switch_to_profile_screen()

    # Функция бросания дайсов

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
