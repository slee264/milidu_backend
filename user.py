from application import app, request, login_manager, db
from flask_login import login_required, login_user, current_user, logout_user
from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/login', methods=['POST'])
def login():
    username = request.get_json()['username']
    password = request.get_json()['password']
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
            return {"message": "유저 확인", {"id": user.id, "name": user.name}}
    return {"message": "유저 확인 실패", "user": None}
    

@app.route('/logout')
@login_required
def logout():
    # logout_user()
    print(current_user.is_authenticated)
    return "logged out"

@app.route('/signup', methods=['POST'])
def signup():

    name = request.get_json()['name']
    username = request.get_json()['username']
    password = request.get_json()['password']
    re_password = request.get_json()['re_password']

    if not (name and username and password and re_password):
        return "모두 입력해주세요"
    elif password != re_password:
        return "비밀번호를 확인해주세요"
    else:
        user = User.signup(name, username, password)

        if user:
            db.session.close()
            # login_user(user)
            return {"message": "유저 가입 완료", "user": {"id": user.id, "name": user.name}}
        return {"message": "유저 가입 실패", "user": None}