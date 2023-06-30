import os
from flask import Flask, request
import requests
from models import bcrypt, db, Cert, CertStats, UniSchedule, UniLecture, User, CertReview, LectureReview
import xml.etree.ElementTree as ET
from flask_login import LoginManager
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
    data = Cert.getAllCerts()
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
        data = CertStats.getAllCertStats()
    else:
        if cert_code is not None:
            if len(cert_code) != 4:
                return "Certification code not valid."
        for digit in cert_code:
            if not digit.isdigit():
                return "Certification code not valid."
        cert_id = Cert.getCertByCode(cert_code).id
        data = CertStats.getCertStatsByCertId(cert_id)
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
    school_name = request.get_json()['name']
    
    if len(school_name) == 0:
        return UniSchedule.getAllSchedules()
    
    school = UniSchedule.getSchedule(school_name)
    
    if school:
        return school

    return UniSchedule.getSimilarSchedules(school_name)

@app.route('/get_lecture', methods=['POST'])
def get_lecture():
    school_name = request.get_json()['name']
    
    if len(school_name) == 0:
        return UniLecture.getAllLectures()
    
    lectures = UniLecture.getLectures(school_name)
    
    return lectures

# 앞으로 이름 더 자세하게 지으세요.
@app.route('/create_cert_review', methods=['POST'])
def create_cert_review():
    cert_name = requests.get_json()['certname']
    cert_id = request.get_json()['cert_id']
    username = request.get_json()['username']
    time_taken = request.get_json()['time_taken']
    difficulty = request.get_json()['difficulty']
    recommend_book = request.get_json()['recommend_book']
    num_attempts = request.get_json()['num_attempts']
    content = request.get_json()['content']
    num_likes = requests.get_json()['num_likes']

    review = CertReview.create(cert_name, cert_id, username, time_taken, difficulty, 
                               recommend_book, num_attempts, content, num_likes)
    
    if review:
        return (review, "리뷰를 성공적으로 작성했습니다.")
    
    return (None, "리뷰 작성 실패")

@app.route('/get_cert_review', methods=['POST'])
def get_review():
    # 글쓴이, 자격증명. 아무것도 적지 않을시 모든 리뷰 리턴.
    category = requests.get_json()['category']
    keyword = requests.get_json()['keyword']
    
    if category == '글쓴이':
        reviews = CertReview.getReviewByUsername(keyword)
        return reviews
    
    elif category == '자격증명':
        reviews = CertReview.getReviewByCertName(keyword)
        return reviews
        
    elif category is None:
        return CertReview.getAllReviews()

@app.route('/create_lect_review', methods=['POST'])
def create_lect_review():
    school_name = request.get_json()['school_name']
    lecture_name = request.get_json()['lecture_name']
    lecture_id = request.get_json()['lecture_id']
    username = request.get_json()['username']
    content = request.get_json()['content']
    num_likes = request.get_json()['num_likes']
    load = request.get_json()['load']
    grade = request.get_json()['grade']
    
    review = LectureReview.create(school_name, lecture_name, lecture_id, username, content, load, grade)
    
    if review:
        return (review, "리뷰를 성공적으로 작성했습니다.")
    return (None, "리뷰 작성 실패")

@app.route('/get_lect_review', methods=['POST'])
def get_lect_review():
    # "글쓴이", "강좌명". 아무것도 적지 않을시 모든 리뷰 리턴.
    category = requests.get_json()['category']
    keyword = requests.get_json()['keyword']
    
    if category == '글쓴이':
        reviews = LectureReview.getReviewByUsername(keyword)
        return reviews
    
    elif category == '강좌명':
        reviews = LectureReview.getReviewByCertName(keyword)
        return reviews
        
    elif category is None:
        return LectureReview.getAllReviews()
    
from user import *
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80')