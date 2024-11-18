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
            print('>>>', token)

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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200


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
        return jsonify({"message": "Friend already added"}), 200


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


@app.route('/profile', methods=['GET'])
@token_required
def profile(current_user):
    user_profile = {'id': current_user['id'],
                    "email": current_user['email'],
                    "username": current_user['username']}
    return jsonify(user_profile)

# Обновление access токена


@app.route('/refresh-token', methods=['POST'])
def refresh_token():
    data = request.json
    refresh_token = data.get('refresh_token')

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


@app.route('/access-token-expiration', methods=['POST'])
def access_token_expiration():
    data = request.json
    if not data:
        return jsonify({'message': 'Invalid JSON format!'}), 400

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


@app.route('/get_questionnaires', methods=['POST'])
def get_questionnaires():
    access_token = request.json.get('access_token')
    user_id = jwt.decode(access_token, ACCESS_TOKEN_SECRET_KEY,
                         algorithms=['HS256'])['user']['id']
    questionnaires = Questionnaire.query.filter_by(user_id=user_id).all()
    return jsonify({'questionnaires': [q.to_dict() for q in questionnaires]}), 200


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


@app.route('/edit_questionnaire', methods=['POST'])
def edit_questionnaire():
    data = request.json
    res = edit_questionnaire_db(data)
    if res is True:
        return jsonify({'message': 'questionnaire was edited'}), 200
    else:
        return jsonify({'message': f'Error: {res}'}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
