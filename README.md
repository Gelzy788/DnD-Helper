# D&D Helper

## 📁 src
__Папка разделяется на 2 основных раздела__
В данной папке хранятся все исполняемые файлы для серверной и клиентской части
#### 1. server
* main.py - главный исполнительный файл со всеми страницами flask-сервера
* database.py - Файл с функциями для взаимодействия с базой данных
* models.py - Файл с моделями таблиц быза дыннх для работы с sqlalchemy
* config.py - Файл с основными константами
* DnD_Helper.sql - База данных с таблицами users, questionnairs, friends, groups

#### 2. client - клиентская часть проекта
* config.py - Файл с основными константами
* main.py - Файл для запуска программы
* friend_manager - Файл с системой дружбы
* group_manager - Файл с системой групп
* login_manager - Файл с системой входа
* main_window - Файл с главным экраном
* profile_manager - Файл с системой взаимодействия с профилем
* questionnaire_manager - ФАйл с системой анкет
* register_manager - Файл с системой регистрации

## 📁 data
### 1. ui_files
* create_questionnaire_screen.ui - Окно для создания новой анкеты
* group_screen.ui - Окно со списком групп пользователя
* login_screen.ui - Окно входа в аккаунт пользователя
* main_screen.ui - Окно главного экрана
* profile_screen.ui - Окно с иформацией об аккаунте
* questionnaire_edit_screen.ui - Окно для редактирования существующей анкеты
* questionnaire_info_screen.ui - Окно с информацией об одной анкете пользователя
* questionnaire_screen.ui - Окно со списком анкет пользователя
* registration_screen.ui - Окно регистрации пользователя
* frends_list_screen.ui - Окно со списком друзей

 
_Для запуска активируйте main.py в директории src/client_