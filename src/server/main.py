from flask import request, jsonify
from flask_login import login_user, logout_user, login_required
from config import *
from database import *
from models import User
from werkzeug.security import check_password_hash
import jwt
from functools import wraps
import datetime
import uuid
import pytz
import datetime


login_manager.init_app(app)


# Декоратор для проверки токена
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Получаем токен из заголовков
        if 'Authorization' in request.headers:
            # Извлекаем токен после "Bearer"
            token = request.headers['Authorization'].split()[1]
            # print('>>>', token)

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Декодируем токен
            data = jwt.decode(token, ACCESS_TOKEN_SECRET_KEY,
                              algorithms=["HS256"])
            current_user = data['user']
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

# Загрузка пользователя


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Вход в аккаунт


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        # login_user(user)
        access_token = jwt.encode({
            'user': {'id': user.id,
                     'email': data['email'],
                     'username': user.username},
            # Время истечения токена
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRATION_TIME)
        }, ACCESS_TOKEN_SECRET_KEY, algorithm="HS256")

        refresh_token = jwt.encode({
            'user_id': user.id,
            'jti': str(uuid.uuid4()),
            # Refresh token на 30 дней
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRATION_TIME),
        }, REFRESH_TOKEN_SECRET_KEY, algorithm="HS256")
        user.refresh_token = refresh_token
        db.session.commit()

        return jsonify({"message": "Login successful", "access_token": f"{access_token}", "refresh_token": f"{refresh_token}"}), 200
    return jsonify({"message": "Invalid credentials"}), 401

# Регистрация аккаунта


@app.route('/registration', methods=['POST'])
def registration():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "email already exists"}), 501
    try:
        add_user(email, password, username)
    except Exception as e:
        print(str(e))
        return jsonify({"message": "registration failed"}), 500
    return jsonify({"message": "registration successful"}), 200

# Выход из аккаунта


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200

# Добавление в друзья


@app.route('/add-friend', methods=['POST'])
def add_friend():
    data = request.json
    user = jwt.decode(data.get('user_token'),
                      ACCESS_TOKEN_SECRET_KEY, algorithms=["HS256"])
    friend_id = data.get('friend_id')
    res = add_friends_db(user['user']['id'], friend_id)
    if res:
        return jsonify({"message": "Friend added"}), 200
    else:
        return jsonify({"message": "Friend already added"}), 501

# Создание новой анкеты


@app.route('/create_new_questionnaire', methods=['POST'])
def create_new_questionnaire():
    data = request.json
    print(data)
    user_id = jwt.decode(data.get(
        'access_token'), ACCESS_TOKEN_SECRET_KEY, algorithms=["HS256"])['user']['id']
    class_name = data.get('class_name')
    species = data.get('species')
    background = data.get('background')
    worldview = data.get('worldview')
    experience = data.get('experience')
    level = data.get('level')
    character_name = data.get('character_name')
    res = add_questionnaire(user_id, class_name, species,
                            background, worldview, experience, level, character_name)
    if res:
        return jsonify({"message": 'questionnaire was created'}), 200
    else:
        return jsonify({'message': "questionnaire wasn't created - error on the side of the add function"}), 401

# Информация о профиле


@app.route('/profile', methods=['GET'])
@token_required
def profile(current_user):
    user_profile = {'id': current_user['id'],
                    "email": current_user['email'],
                    "username": current_user['username']}
    print(user_profile)
    return jsonify(user_profile)

# Обновление access токена


@app.route('/refresh-token', methods=['POST'])
def refresh_token():
    data = request.json
    refresh_token = data.get('refresh_token')
    print(refresh_token)

    if not refresh_token:
        return jsonify({'message': 'Refresh token is missing!'}), 401

    try:
        data = jwt.decode(
            refresh_token, REFRESH_TOKEN_SECRET_KEY, algorithms=["HS256"])
        user_id = data['user_id']
        jti = data['jti']  # Извлечение UUID из токена
        user = User.query.get(user_id)

        if user and user.refresh_token == refresh_token:
            new_access_token = jwt.encode({
                'user': {'id': user.id, 'email': user.email, 'username': user.username},
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRATION_TIME)
            }, ACCESS_TOKEN_SECRET_KEY, algorithm="HS256")

            return jsonify({"access_token": f"{new_access_token}"}), 200
        else:
            return jsonify({'message': 'Invalid refresh token!'}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Refresh token expired!'}), 401
    except Exception as e:
        return jsonify({'message': 'Invalid refresh token!'}), 401

# Получение информации об актуальности access токена


@app.route('/access-token-expiration', methods=['POST'])
def access_token_expiration():
    data = request.json
    if not data:
        return jsonify({'message': 'Invalid JSON format!'}), 400
    print(data)
    access_token = data.get('access_token')
    if not access_token:
        return jsonify({'message': 'Access token is missing!'}), 401

    try:
        # Декодируем токен
        decoded_token = jwt.decode(
            access_token, ACCESS_TOKEN_SECRET_KEY, algorithms=["HS256"])
        expiration_time = decoded_token.get('exp')

        if expiration_time:
            current_time = datetime.datetime.now(pytz.UTC)
            expiration_datetime = datetime.datetime.fromtimestamp(
                expiration_time, pytz.UTC)
            is_valid = current_time < expiration_datetime
            return jsonify({"is_valid": is_valid}), 200
        else:
            return jsonify({'message': 'Expiration time not found in token!'}), 400
    except jwt.ExpiredSignatureError:
        return jsonify({"is_valid": False}), 200
    except Exception as e:
        print(str(e))
        return jsonify({'message': 'Invalid access token!'}), 401

# Получение информации об актуальности refresh токена


@app.route('/refresh-token-expiration', methods=['POST'])
def refresh_token_expiration():
    data = request.json
    if not data:
        return jsonify({'message': 'Invalid JSON format!'}), 400

    refresh_token = data.get('refresh_token')
    if not refresh_token:
        return jsonify({'message': 'Refresh token is missing!'}), 401

    try:
        # Декодируем токен
        decoded_token = jwt.decode(
            refresh_token, REFRESH_TOKEN_SECRET_KEY, algorithms=["HS256"])
        expiration_time = decoded_token.get('exp')

        if expiration_time:
            current_time = datetime.datetime.now(pytz.UTC)
            expiration_datetime = datetime.datetime.fromtimestamp(
                expiration_time, pytz.UTC)
            is_valid = current_time < expiration_datetime
            return jsonify({"is_valid": is_valid}), 200
        else:
            return jsonify({'message': 'Expiration time not found in token!'}), 400
    except jwt.ExpiredSignatureError:
        return jsonify({"is_valid": False}), 200
    except Exception as e:
        print(str(e))
        return jsonify({'message': 'Invalid refresh token!'}), 401

# Получение списка анкет


@app.route('/get_questionnaires', methods=['POST'])
def get_questionnaires():
    access_token = request.json.get('access_token')
    user_id = jwt.decode(access_token, ACCESS_TOKEN_SECRET_KEY,
                         algorithms=['HS256'])['user']['id']
    questionnaires = Questionnaire.query.filter_by(user_id=user_id).all()
    return jsonify({'questionnaires': [q.to_dict() for q in questionnaires]}), 200

# Удаление анкеты


@app.route('/del_questionnaire', methods=['POST'])
def del_questionnaire():
    print('Подключение')
    print(request.json.get('id'))
    try:
        questionnaire_id = request.json.get('id')
        delete_questionnaire(questionnaire_id)
        return jsonify({'message': 'questionnaire was deleted'})
    except Exception as e:
        print(str(e))
        return jsonify({'message': f'Error: {str(e)}'})

# Редактирование анкеты


@app.route('/edit_questionnaire', methods=['POST'])
def edit_questionnaire():
    data = request.json
    res = edit_questionnaire_db(data)
    if res is True:
        return jsonify({'message': 'questionnaire was edited'}), 200
    else:
        return jsonify({'message': f'Error: {res}'}), 400

# Получение списка друзей


@app.route('/get_friends', methods=['POST'])
def get_friends():
    access_token = request.json.get('access_token')
    user_id = jwt.decode(access_token, ACCESS_TOKEN_SECRET_KEY,
                         algorithms=['HS256'])['user']['id']
    friend_list = Friends.query.filter_by(user_id=user_id).all()
    friend_list.extend(Friends.query.filter_by(friend_id=user_id).all())
    return jsonify({'friends': [q.to_dict() for q in friend_list]}), 200

# Обновление статуса дружбы


@app.route('/update_friendship_status', methods=['POST'])
def update_friendship_status():
    request_id = request.json.get('request_id')
    res = update_friendship_status_db(request_id)

    if res is True:
        return jsonify({'message': 'status was update'}), 200
    else:
        return jsonify({'message': f'Error: {res}'})

# Удаление приглашения в друзья


@app.route('/delete_friend_request', methods=['POST'])
def delete_friend_request():
    request_id = request.json.get('request_id')
    print(request_id)
    res = delete_friend_request_db(request_id)

    if res is True:
        return jsonify({'message': 'status was update'}), 200
    else:
        return jsonify({'message': f'Error: {res}'})

# Получение списка групп


@app.route('/get_groups', methods=['POST'])
def get_groups():
    access_token = request.json.get('access_token')
    user_id = jwt.decode(access_token, ACCESS_TOKEN_SECRET_KEY,
                         algorithms=['HS256'])['user']['id']
    owner_groups = Groups.query.filter_by(owner_id=user_id).all()
    participant_groups = GroupsMembers.query.filter_by(user_id=user_id).all()
    return jsonify({'user owner groups': [i.to_dict() for i in owner_groups], 'user participant groups': [i.to_dict() for i in participant_groups]}), 200

# Создание группы


@app.route('/create_group', methods=['POST'])
def create_group():
    data = request.json
    user_id = jwt.decode(data.get(
        'access_token'), ACCESS_TOKEN_SECRET_KEY, algorithms=['HS256'])['user']['id']
    group_name = data.get('name')
    res = create_group_db(group_name, user_id)
    if res is True:
        return jsonify({'message': 'group was created'}), 200
    else:
        return jsonify({'message': f'Error: {res}'}), 401

# Добавление пользователя в группу


@app.route('/add_user_to_group', methods=['POST'])
def add_user_to_group():
    data = request.json
    user_id = jwt.decode(data.get(
        'access_token'), ACCESS_TOKEN_SECRET_KEY, algorithms=['HS256'])['user']['id']
    group_id = data.get('group_id')
    res = add_user_to_group_db(user_id, group_id)
    if res is True:
        return jsonify({'message': 'user was added to group'}), 200
    elif res is False:
        return jsonify({'message': 'The user has already been added to the group'}), 401
    else:
        return jsonify({'message': f'Error: {res}'}), 401

# Получение ника админа


@app.route('/get_owner_username', methods=['POST'])
def get_owner_username():
    group_id = request.json.get('group_id')
    owner_id = Groups.query.filter_by(id=group_id).first().owner_id
    user = User.query.filter_by(id=owner_id).first()
    if user:
        return jsonify({'username': user.username}), 200

# Получение информации о группе


@app.route('/get_group_info', methods=['POST'])
def get_group_info():
    group_id = request.json.get('group_id')
    group = Groups.query.filter_by(id=group_id).first()
    next_game_date = group.game_date.isoformat(
    ) if group.game_date else None  # Преобразуем дату в строку
    members = GroupsMembers.query.filter_by(group_id=group_id).all()
    return jsonify({'members': [i.to_dict() for i in members], 'game_date': next_game_date}), 200

# @app.route('/get_group_info', methods=['POST'])
# def get_group_members():
#     group_id = request.json.get('group_id')
#     group = Groups.query.filter_by(id=group_id).first()
#     members = GroupsMembers.query.filter_by(group_id=group_id).all()
#     return jsonify({'members': [i.to_dict() for i in members]}), 200

# Получение сюжета игры


@app.route('/get_plot', methods=['POST'])
def get_plot():
    group_id = request.json.get('group_id')
    group = Groups.query.filter_by(id=group_id).first()
    return jsonify({'plot': group.plot}), 200

# Сохранение отредактированного сюжета


@app.route('/edit_plot', methods=['POST'])
def edit_plot():
    group_id = request.json.get('group_id')
    plot = request.json.get('plot')
    res = edit_plot_db(group_id, plot)
    if res is True:
        return jsonify({'message': 'plot has been edited'}), 200
    else:
        return jsonify({'message': f'Error: {res}'}), 401

# Постановка даты ближайшей игры


@app.route('/set_game_date', methods=['POST'])
def set_game_date():
    group_id = request.json.get('group_id')
    date = request.json.get('date')
    res = set_game_date_db(group_id, date)

    if res is True:
        return jsonify({'message': 'date has been updated'}), 200
    else:
        return jsonify({'message': f'Error: {res}'}), 401

# Привязка анкеты к группе


@app.route('/connect_questionnaire', methods=['POST'])
def connect_member_questionnaire():
    group_id = request.json.get('group_id')
    user_id = jwt.decode(request.json.get(
        'access_token'), ACCESS_TOKEN_SECRET_KEY, algorithms=['HS256'])['user']['id']
    questionnaire_id = request.json.get('questionnaire_id')
    res = connect_questionnaire_db(user_id, group_id, questionnaire_id)

    if res is True:
        return jsonify({'message': 'questionnaire has been updated'}), 200
    else:
        return jsonify({'message': f'Error: {res}'}), 401

# Удаление игрока из группы


@app.route('/kick_member', methods=['POST'])
def kick_member():
    group_id = request.json.get('group_id')
    member_id = request.json.get('member_id')
    res = kick_member_db(group_id, member_id)

    if res is True:
        return jsonify({'message': 'user has been kicked'}), 200
    else:
        return jsonify({'message': f'Error: {res}'}), 401

# Удаление группы *НЕ ДОДЕЛАНО*


@app.route('/delete_group', methods=['POST'])
def delete_member():
    group_id = request.json.get('group_id')
    res = delete_group_db(group_id)

    if res is True:
        return jsonify({'message': 'group has been deleted'}), 200
    else:
        return jsonify({'message': f'Error: {res}'}), 401

# Сохранение аватара анкеты


@app.route('/upload-questionnaire-image/<int:questionnaire_id>', methods=['POST'])
def upload_questionnaire_image(questionnaire_id):
    if 'image' not in request.files:
        return jsonify({'message': 'No image part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(image_path)

    if save_questionnaire_image(questionnaire_id, image_path):
        return jsonify({'message': 'Image uploaded successfully'}), 200
    return jsonify({'message': 'Failed to save image'}), 500

# Получение аватара анкеты


@app.route('/get-questionnaire-image/<int:questionnaire_id>', methods=['GET'])
def get_questionnaire_image_route(questionnaire_id):
    image_path = get_questionnaire_image(questionnaire_id)
    if image_path:
        return jsonify({'image_path': image_path}), 200
    return jsonify({'message': 'Image not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
