from application import app, request, login_manager, jsonify
from flask_login import login_required, login_user, current_user, logout_user

from models import User
from util import serialize

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/signup', methods=['POST'])
def signup():
    if request.is_json:
        name = request.get_json().get('name', None)
        username = request.get_json().get('username', None)
        password = request.get_json().get('password', None)
        
        if name and username and password:
            user = User.signup(name, username, password)
            
            if user:
                return jsonify(user), 200
            return jsonify("유저 등록 실패"), 404
        return jsonify("잘못된 정보"), 404
        
    return jsonify("잘못된 요청"), 500

@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        username = request.get_json().get('username', None)
        password = request.get_json().get('password', None)
        def validate(username, password):
            def validate_username(username):
                # 임시
                if username:
                    return True
                return False
            def validate_pw(password):
                # 임시
                if password:
                    return True
                return False

            return validate_username(username) and validate_pw(password)

        if validate(username, password):
            user = User.authenticate(username, password)
            if user:
                # login_user(user)
                return jsonify(user), 200
            return jsonify("로그인 실패"), 404
        return jsonify("정보를 다시 확인하세요."), 404
    return jsonify("잘못된 요청"), 500
    

@app.route('/logout')
@login_required
def logout():
    # logout_user() 
    print(current_user.is_authenticated)
    return "logged out"