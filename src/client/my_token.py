import requests
from config import *

# @staticmethod


def token_required(func):
    def wrapper(self, *args, **kwargs):
        try:
            with open('tokens.txt', 'r') as f:
                data = f.readlines()
                access_token = data[0].strip()
                refresh_token = data[1].strip()
        except Exception as e1:
            print('ОШИБКА')
            self.main_window.stacked_widget.setCurrentWidget(
                self.main_window.main_window)
            return
        if not is_access_token_expiring_soon():
            print("Токен истекает, обновляем...")
            refresh_access_token()
        if access_token == '':
            print("Токен недействителен, перенаправляем на экран входа...")
            self.main_window.stacked_widget.setCurrentWidget(
                self.main_window.login_manager)
            return
        return func(self, *args, **kwargs)
    return wrapper

# def token_required(func):
#     def wrapper(self, *args, **kwargs):
#         # Проверяем, есть ли уже сохраненные токены
#         if not hasattr(self, 'access_token') or not hasattr(self, 'refresh_token'):
#             try:
#                 with open('tokens.txt', 'r') as f:
#                     data = f.readlines()
#                     self.access_token = data[0].strip()
#                     self.refresh_token = data[1].strip()
#             except Exception as e1:
#                 print('ОШИБКА')
#                 self.main_window.stacked_widget.setCurrentWidget(
#                     self.main_window.main_window)
#                 return

    #     if not is_access_token_expiring_soon():
    #         print("Токен истекает, обновляем...")
    #         refresh_access_token()

    #     if self.access_token == '':
    #         print("Токен недействителен, перенаправляем на экран входа...")
    #         self.main_window.stacked_widget.setCurrentWidget(
    #             self.main_window.login_manager)
    #         return

    #     return func(self, *args, **kwargs)
    # return wrapper


def refresh_access_token():
    response = requests.post(
        f'http://{IP_ADDRESS}:{PORT}/refresh-token', json={'refresh_token': refresh_token})

    if response.status_code == 200:
        try:
            json_response = response.json()
            access_token = json_response.get('access_token')
            # refresh_token = json_response.get('refresh_token')
            with open('tokens.txt', 'w') as f:
                f.write(access_token)
                f.write('\n')
                f.write(refresh_token)
        except ValueError:
            print("Ошибка декодирования JSON: пустой или некорректный ответ")
    else:
        try:
            print(response.json().get('message'))
        except ValueError:
            print("Ошибка декодирования JSON: пустой или некорректный ответ")
        print("Некорректный ответ от сервера или ошибка соединения")


def is_access_token_expiring_soon():
    response = requests.post(
        f'http://{IP_ADDRESS}:{PORT}/access-token-expiration',
        json={'access_token': access_token})

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
