import os
from flask import Flask, request
import requests
from models import bcrypt, db, Cert, CertStats, UniSchedule, UniLecture, User
import xml.etree.ElementTree as ET
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from config import SECRET_KEY, DB_SERVICE_KEY
app = Flask("app")
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
# 임시!!!!!
app.secret_key = SECRET_KEY

db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/certs', methods=['GET'])
def certs():
    data = Cert.query.all()
    certlist = []
    for cert in data:
        val = {'name': cert.name, 'name_eng': cert.name_eng, 'code': cert.code, 'ministry': cert.ministry, 'host': cert.host, 'majors': cert.related_majors }
        certlist.append(val)
    return certlist

@app.route('/stats', methods=['GET'])
def stats():
    cert_code = request.args.get('cert_code', None)
    data = None
    if cert_code is None:
        data = CertStats.query.all()
    else:
        if cert_code is not None:
            if len(cert_code) != 4:
                return "Certification code not valid."
        for digit in cert_code:
            if not digit.isdigit():
                return "Certification code not valid."
        cert_id = Cert.query.filter(Cert.code == cert_code).first().id
        data = CertStats.query.filter(CertStats.cert_id == cert_id).all()
    statslist = []
    for stats in data:
        if stats.total_taken is not 0:
            val = {'name': stats.name, 'year': stats.year, 'test_taken': stats.total_taken, 'test_passed': stats.total_passed, 'pass_rate': stats.total_passed * 100 / stats.total_taken}
            statslist.append(val)
        else:
            val = {'name': stats.name, 'year': stats.year, 'test_taken': stats.total_taken, 'test_passed': stats.total_passed, 'pass_rate': 0}
            statslist.append(val)
    return statslist

@app.route('/schedule', methods=['POST'])
def schedule():
    cert_code = request.args.get('cert_code', None)

    if cert_code is not None:
        if len(cert_code) != 4:
            return "Certification code not valid."
        for digit in cert_code:
            if not digit.isdigit():
                return "Certification code not valid."
    else:
        return "Certification code not provided. '.../schedule?cert_code={CERTIFICATION CODE}'"
    BODY = 1
    ITEMS = 0
    schedule_xml_url = 'http://openapi.q-net.or.kr/api/service/rest/InquiryTestInformationNTQSVC/getJMList'
    schedule_xml_params ={'serviceKey' : DB_SERVICE_KEY, 'jmCd' : cert_code}
    schedule_xml = requests.get(schedule_xml_url, params=schedule_xml_params)
    schedule_xml_root = ET.fromstring(schedule_xml.content)
    schedule_list = []
    for item in schedule_xml_root[BODY][ITEMS]:
        schedule = {}
        if item.find("implplannm") is not None:
            schedule['회차'] = item.find("implplannm").text
        else:
            schedule['회차'] = ""
        if item.find("jmfldnm") is not None:
            schedule['종목명'] = item.find("jmfldnm").text
        else:
            schedule['종목명'] = ""
        if item.find("docregstartdt") is not None:
            schedule['필기원서접수시작'] = item.find("docregstartdt").text
        else:
            schedule['필기원서접수시작'] = ""
        if item.find("docregenddt") is not None:
            schedule['필기원서접수종료'] = item.find("docregenddt").text
        else:
            schedule['필기원서접수종료'] = ""
        if item.find("docexamstartdt") is not None:
            schedule['필기시작'] = item.find("docexamstartdt").text
        else:
            schedule['필기시작'] = ""
        if item.find("docexamenddt") is not None:
            schedule['필기종료'] = item.find("docexamenddt").text
        else:
            schedule['필기종료'] = ""
        if item.find("docpassdt") is not None:
            schedule['필기합격발표'] = item.find("docpassdt").text
        else:
            schedule['필기합격발표'] = ""
        if item.find("docsubmitstartdt") is not None:
            schedule['자격서류제출시작'] = item.find("docsubmitstartdt").text
        else:
            schedule['자격서류제출시작'] = ""
        if item.find("docsubmitenddt") is not None:
            schedule['자격서류제출종료'] = item.find("docsubmitenddt").text
        else:
            schedule['자격서류제출종료'] = ""
        if item.find("pracregstartdt") is not None:
            schedule['실기원서접수시작'] = item.find("pracregstartdt").text
        else:
            schedule['실기원서접수시작'] = ""
        if item.find("pracregenddt") is not None:
            schedule['실기원서접수종료'] = item.find("pracregenddt").text
        else:
            schedule['실기원서접수종료'] = ""
        if item.find("pracexamstartdt") is not None:
            schedule['실기시작'] = item.find("pracexamstartdt").text
        else:
            schedule['실기시작'] = ""
        if item.find("pracexamenddt") is not None:
            schedule['실기종료'] = item.find("pracexamenddt").text
        else:
            schedule['실기종료'] = ""
        if item.find("pracpassstartdt") is not None:
            schedule['합격발표시작'] = item.find("pracpassstartdt").text
        else:
            schedule['합격발표시작'] = ""
        if item.find("pracpassenddt") is not None:
            schedule['합격발표종료'] = item.find("pracpassenddt").text
        else:
            schedule['합격발표종료'] = ""
        schedule_list.append(schedule)

    return schedule_list

@app.route('/get_unischedule', methods=['POST'])
def get_uni():
    name = request.get_json()['name']
    
    if len(name) == 0:
        return UniSchedule.query.all()
    
    school = UniSchedule.query.filter(UniSchedule.school_name == name).first()
    
    if school:
        return school
    
    else:
        schools = UniSchedule.query.filter(UniSchedule.school_name[0] == name[0]).all()
        return schools

@app.route('/get_lecture', methods=['POST'])
def get_lecture():
    name = request.get_json()['name']
    
    if len(name) == 0:
        return UniLecture.query.all()
    
    lectures = UniLecture.query.filter(UniLecture.univ == name).all()
    
    if lectures:
        return lectures
        
    return "Lecture not found"

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
            print("username validated")
            return True
        def validate_pw(password):
            # 임시
            print("password validated")
            return True

        return validate_username(username) and validate_pw(password)

    if validate(username, password):
        print("hi")
        user = User.authenticate(username, password)
        if user:
            login_user(user)
            print(current_user.is_authenticated)
        else:
            print('login_failed')
    return 'login test'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    print(current_user.sepis_authenticated)
    return "logged out"

@app.route('/register', methods=['POST'])
def register():

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
            # login_user(user)
            return "회원가입 완료"

        else:
            return "오류"

    return "register test"

# 앞으로 이름 더 자세하게 지으세요.
# @app.route('/certreview', methods=['POST'])
# def certreview():
#     certid = request.get_json()['certid']
#     username = request.get_json()['username']
#     time_taken = request.get_json()['time_taken']
#     difficulty = request.get_json()['difficulty']
#     recommend_book = request.get_json()['recommend_book']
#     num_attempts = request.get_json()['num_attempts']
#     content = request.get_json()['content']

    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80')
