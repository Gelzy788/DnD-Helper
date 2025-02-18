
from config import db, app
from models import *
import os
from sqlalchemy import update, delete
from config import db
from models import User
from werkzeug.security import generate_password_hash
from datetime import datetime

# Добавление нового пользователя в бд


def add_user(email, password, username):
    # Хэшируем пароль перед сохранением
    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password=hashed_password, username=username)
    db.session.add(new_user)
    db.session.commit()

# Удаление анкеты из бд


def delete_questionnaire(questionnaire_id):
    questionnaire = db.session.query(
        Questionnaire).filter_by(id=questionnaire_id).first()
    db.session.delete(questionnaire)
    db.session.commit()

# Добавление анкеты в дб


def add_questionnaire(user_id, class_name, species, background, worldview, experience, level, character_name):
    new_questionnaire = Questionnaire(user_id=user_id, class_name=class_name, species=species, background=background,
                                      worldview=worldview, experience=experience, level=level, character_name=character_name)
    try:
        db.session.add(new_questionnaire)
        db.session.commit()
        return True
    except Exception as e:
        print(str(e))
        return False

# ИЗменение анкеты в бд


def edit_questionnaire_db(new_data):
    # Получаем ID анкеты, которую нужно обновить
    questionnaire_id = new_data.get('id')

    # Создаем запрос на обновление
    stmt = (
        update(Questionnaire)
        # Используем атрибут напрямую
        .where(Questionnaire.id == questionnaire_id)
        .values(
            class_name=new_data.get('class_name'),
            species=new_data.get('species'),
            background=new_data.get('background'),
            worldview=new_data.get('worldview'),
            experience=new_data.get('experience'),
            level=new_data.get('level'),
            character_name=new_data.get('name')  # Исправлено на character_name
        )
    )

    try:
        db.session.execute(stmt)  # Выполняем запрос
        db.session.commit()  # Зафиксируйте изменения
        return True
    except Exception as e:
        print('ОТКАТЫВАЮ ИЗМЕНЕНИЯ...')
        db.session.rollback()  # Откатите изменения в случае ошибки
        return str(e)  # Возвращаем сообщение об ошибке


# Создание пары друзей в бд
def add_friends_db(user_id, friend_id):
    if not Friends.query.filter_by(user_id=user_id, friend_id=friend_id).first() and not Friends.query.filter_by(user_id=friend_id, friend_id=user_id).first():
        new_couple = Friends(user_id=user_id, friend_id=friend_id)
        try:
            db.session.add(new_couple)
            db.session.commit()
            return True
        except Exception as e:
            print("ОШИБКА")
            return False
    else:
        print("Already friends")
        return False

# Удаление пользователя из бд


def delete_user(email, password, username):
    user = User(email=email, password=password, username=username)

    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as err:
        print("User error: ", err)

# Обновление статусы дружбы в бд


def update_friendship_status_db(request_id):
    # print(request_id, '>>', Friends.query.filter_by(id=request_id).first())
    if Friends.query.filter_by(id=request_id).first().status == 0:
        stmt = (
            update(Friends)
            .where(Friends.id == request_id)
            .values(
                status=1
            )
        )
    else:
        stmt = delete(Friends).where(Friends.id == request_id)

    try:
        db.session.execute(stmt)  # Выполняем запрос
        db.session.commit()  # Зафиксируйте изменения
        return True
    except Exception as e:
        print('ОТКАТЫВАЮ ИЗМЕНЕНИЯ...')
        db.session.rollback()  # Откатите изменения в случае ошибки
        return str(e)  # Возвращаем сообщение об ошибке

# Удаление предложения в друзья


def delete_friend_request_db(request_id):
    stmt = delete(Friends).where(Friends.id == request_id)

    try:
        db.session.execute(stmt)  # Выполняем запрос
        db.session.commit()  # Зафиксируйте изменения
        return True
    except Exception as e:
        print('ОТКАТЫВАЮ ИЗМЕНЕНИЯ...')
        db.session.rollback()  # Откатите изменения в случае ошибки
        return str(e)  # Возвращаем сообщение об ошибке

# Добавление группы в бд


def create_group_db(name, owner_id):
    group = Groups(name=name, owner_id=owner_id)

    try:
        db.session.add(group)
        db.session.commit()
        return True
    except Exception as e:
        return str(e)

# Добавление пользователя в группу в бд


def add_user_to_group_db(user_id, group_id):
    if not GroupsMembers.query.filter_by(group_id=group_id, user_id=user_id):
        new_member = GroupsMembers(group_id=group_id, user_id=user_id)

        try:
            db.session.add(new_member)
            db.session.commit()
            return True
        except Exception as e:
            return str(e)
    else:
        return False

# Редактирование сбжета игры в бд


def edit_plot_db(group_id, plot):
    stmt = update(Groups).where(Groups.id == group_id).values(plot=plot)

    try:
        db.session.execute(stmt)
        db.session.commit()
        return True
    except Exception as e:
        print('ОТКАТЫВАЮ ИЗМЕНЕНИЯ...')
        db.session.rollback()
        return str(e)

# ПОстановка даты следующей игры в бд


def set_game_date_db(group_id, date):
    next_game_date = datetime.strptime(date, '%d-%m-%Y').date()
    stmt = update(Groups).where(Groups.id == group_id).values(
        game_date=next_game_date)

    try:
        db.session.execute(stmt)
        db.session.commit()
        return True
    except Exception as e:
        print('ОТКАТЫВАЮ ИЗМЕНЕНИЯ...')
        print(str(e))
        db.session.rollback()
        return str(e)

# Присоединение анкеты к группе в бд


def connect_questionnaire_db(user_id, group_id, questionnaire_id):
    print(user_id)
    stmt = update(GroupsMembers).where(GroupsMembers.group_id == group_id,
                                       GroupsMembers.user_id == user_id).values(member_questionnaire_id=questionnaire_id)

    try:
        db.session.execute(stmt)
        db.session.commit()
        return True
    except Exception as e:
        print('ОТКАТЫВАЮ ИЗМЕНЕНИЯ...')
        print(str(e))
        db.session.rollback()
        return str(e)

# Удаление пользователя из группы в бд


def kick_member_db(group_id, user_id):
    member = db.session.query(GroupsMembers).filter_by(
        group_id=group_id, user_id=user_id).first()
    try:
        db.session.delete(member)
        db.session.commit()
        return True
    except Exception as e:
        print('ОТКАТЫВАЮ ИЗМЕНЕНИЯ...')
        print(str(e))
        db.session.rollback()
        return str(e)

# Удаление группы в бд (Не доделоано)


def delete_group_db(group_id):
    group = db.session.query(Groups).filter_by(id=group_id).first()
    try:
        db.session.delete(group)
        db.session.commit()
        return True
    except Exception as e:
        print('ОТКАТЫВАЮ ИЗМЕНЕНИЯ...')
        print(str(e))
        db.session.rollback()
        return str(e)

# Сохранение пути к аватарке анкеты в бд


def save_questionnaire_image(questionnaire_id, image_path):
    questionnaire = db.session.query(
        Questionnaire).filter_by(id=questionnaire_id).first()
    if questionnaire:
        questionnaire.avatar_url = image_path
        db.session.commit()
        return True
    return False

# Получение пути к аватарке анкеты из бд


def get_questionnaire_image(questionnaire_id):
    questionnaire = db.session.query(
        Questionnaire).filter_by(id=questionnaire_id).first()
    if questionnaire:
        return questionnaire.avatar_urlo  # +Y76PL7?byxr
    return None

# Обновление пути к аватарке пользователя (Не реализовано)


def update_profile_picture(user_id, profile_picture):
    user = User.query.get(user_id)
    if user:
        # Удаляем старое фото профиля, если оно существует
        if user.profile_picture and user.profile_picture != 'default.png':
            old_image_path = os.path.join(
                app.config['UPLOAD_FOLDER'], user.profile_picture)
            if os.path.exists(old_image_path):
                os.remove(old_image_path)

        user.profile_picture = profile_picture
        try:
            db.session.commit()
        except Exception as err:
            print("Error updating profile picture: ", err)
