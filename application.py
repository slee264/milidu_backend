import os
from flask import Flask, request, jsonify
import requests
import xml.etree.ElementTree as ET
from flask_login import LoginManager


from models import bcrypt, Cert, CertStats, UniSchedule, UniLecture, User, CertReview, LectureReview, CertLecture
from config import DB_SERVICE_KEY
from __init__ import create_app
from util import serialize, frequency_sort
from database import db_session
from operator import itemgetter

app = create_app()

# db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
app.json.ensure_ascii = False

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/certs', methods=['GET'])
def certs():
    data = Cert.getAllCerts()
    certlist = []
    #합격률, 응시자수
    for cert in data:
        val = {'id': cert.id, 'name': cert.name, 'code': cert.code, 'majors': cert.related_majors, 'year': 0, 'total_passed': 0, 'total_taken': 0}
        certlist.append(val)
        
    for cert in certlist:
        stat = CertStats.getCertStatsByCertId(cert['id'])
        if stat:
            cert['year'] = stat[-1].year
            cert['total_passed'] = stat[-1].total_passed
            cert['total_taken'] = stat[-1].total_taken
    datalist = sorted(certlist, key = itemgetter('total_taken'), reverse=True)
    print(datalist)
    
    return jsonify(datalist), 200

@app.route('/cert_stats', methods=['GET'])
def stats():
    cert_code = request.args.get('cert_code')
    data = None
    if cert_code is None:
        data = CertStats.getAllCertStats()
        cert_info = ""
        lecture_info = ""
    else:
        if cert_code is not None:
            if len(cert_code) != 4:
                return jsonify({'message': "Certification code is four digits. '.../stats?cert_code={CERTIFICATION CODE}'"}), 404
        for digit in cert_code:
            if not digit.isdigit():
                return jsonify({'message': "Certification code only consists of digits. '.../stats?cert_code={CERTIFICATION CODE}'"}), 404
        
        cert = Cert.getCertByCode(cert_code)
        if cert is None:
            return jsonify({'message': "Certification not found. '.../stats?cert_code={CERTIFICATION CODE}'"}), 404
        data = CertStats.getCertStatsByCertId(cert.id)
        cert = Cert.getCertByCode(cert_code)
        info = CertLecture.query.filter(CertLecture.cert_name == cert.name).all()
        lecture_list = []
        if info:
            for lecture in info:
                lecture_info = {'lecture_name': lecture.lecture_name, 'teacher':lecture.teacher, 'url': lecture.url}
                lecture_list.append(lecture_info)
        else:
            lecture_info = ""
        cert_info = {'name': cert.name, 'name_eng': cert.name_eng, 'ministry': cert.ministry, 'host': cert.host, 'description': cert.description}
    stats_list = []
    for stats in data:
        val = {'name': stats.name, 'year': stats.year, 'test_taken': stats.total_taken, 'test_passed': stats.total_passed, 'military_taken': stats.total_taken_m, 'military_passed': stats.total_passed_m}
        val['pass_rate'] = stats.total_passed * 100 / stats.total_taken if stats.total_taken is not 0 else 0
        stats_list.append(val)
    review_data = CertReview.getReviewByCertCode(cert_code)
    book_list = []
    book_frequency_rank = []
    if review_data:
        for review in review_data:
            book_list.append(review.recommend_book)
        book_frequency_rank = frequency_sort(book_list)
    return jsonify({"cert_info": cert_info, "lecture_info": lecture_list, "data": stats_list, "recommend_book": book_frequency_rank}), 200

@app.route('/cert_test_schedule', methods=['POST'])
def schedule():
    cert_code = request.get_json().get('cert_code', None)
    if cert_code is not None:
        if len(cert_code) != 4:
            return jsonify({'message': "Certification code needs to be four digits. '.../schedule?cert_code={CERTIFICATION CODE}'"}), 404
        for digit in cert_code:
            if not digit.isdigit():
                return jsonify({'message': "Certification code only consists of digits. '.../schedule?cert_code={CERTIFICATION CODE}'"}), 404
    else:
        return jsonify({'message': "Certification not valid. '.../stats?cert_code={CERTIFICATION CODE}'"}), 404
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

    return jsonify(schedule_list), 200
    # elif schedule_list is None:
    #     return jsonify({'message': "Certification found. '.../stats?cert_code={CERTIFICATION CODE}'"}), 404

        
    # return jsonify(schedule_list), 200 if schedule_list else jsonify({'message': "Certification found. '.../\
#                         stats?cert_code={CERTIFICATION CODE}'"}), 404

@app.route('/get_unischedule', methods=['POST'])
def get_uni():
    school_name = None
    if request.is_json and request.get_json().get('school_name', None):
        school_name = request.get_json().get('school_name', None)
    
    if school_name is None:
        all_information = UniSchedule.getAllSchedules()
        school_info = serialize(all_information)
        school_list = []
        for data in school_info:
            school_name = data['school_name']
            school_id = data['id']
            school_list.append({"school_name": school_name, "school_id": school_id})
        return jsonify(school_list), 200

    schedule = UniSchedule.getSchedule(school_name)
    
    if schedule:
        return jsonify(serialize(schedule)), 200

    schedule = UniSchedule.getSimilarSchoolSchedules(school_name)
    return jsonify(serialize(schedule)), 200

@app.route('/get_lecture', methods=['POST'])
def get_lecture():
    school_name = None
    if request.is_json and request.get_json().get('school_name', None):
        school_name = request.get_json().get('school_name', None)
        
    if school_name is None:
        return jsonify(serialize(UniLecture.getAllLectures())), 200
    
    lectures = UniLecture.getLectures(school_name)
    return jsonify(serialize(lectures)), 200

# 앞으로 이름 더 자세하게 지으세요.
@app.route('/create_cert_review', methods=['POST'])
def create_cert_review():
    if request.is_json:
        cert_name = request.get_json().get('cert_name', None)
        cert_code = request.get_json().get('cert_code', None)
        username = request.get_json().get('username', None)
        time_taken = request.get_json().get('time_taken', None)
        difficulty = request.get_json().get('difficulty', None)
        recommend_book = request.get_json().get('recommend_book', None)
        num_attempts = request.get_json().get('num_attempts', None)
        content = request.get_json().get('content', None)
        study_method = request.get_json().get('study_method', None)
        major = request.get_json().get('major', None)
        sex = request.get_json().get('sex', None)
        birthday = request.get_json().get('birthday', None)

        if (cert_name and cert_code and username and 
            time_taken and difficulty and 
            recommend_book and num_attempts and
            content and study_method):
            review = CertReview.create(cert_name, cert_code, username, time_taken, difficulty, 
                               recommend_book, num_attempts, content, study_method, major, sex, birthday)
        else:
            return jsonify("정보 다 입력하세요"), 404

        if review:
            # review.pop('_sa_instance_state', None)
            return jsonify(serialize(review)), 200
    return jsonify("잘못된 요청"), 404


@app.route('/get_cert_review', methods=['POST'])
def get_cert_review():
    # 글쓴이, 자격증명. 아무것도 적지 않을시 모든 리뷰 리턴.
    if request.is_json:
        category = request.get_json().get('category', None)
        keyword = request.get_json().get('keyword', None)
        if category == '글쓴이':
            reviews = CertReview.getReviewByUsername(keyword)
            return jsonify(serialize(reviews)), 200

        elif category == '자격증코드':
            COUNT = 0
            total_sum_difficulty = total_sum_num_attempts = total_sum_time_taken = average_difficulty = average_num_attempts = average_time_taken = 0
            reviews = CertReview.getReviewByCertCode(keyword)
            for data in reviews:
                whole_time = data.time_taken
                step1 = whole_time.split('년')
                year = step1.pop(0)
                step2 = step1[0].split('개월')
                month = step2.pop(0)
                step3 = step2[0].split('주')
                week = step3.pop(0)
                total_week = 52 * int(year) + 4 * int(month) + int(week)
                COUNT += 1
                total_sum_difficulty += data.difficulty
                total_sum_num_attempts += data.num_attempts
                total_sum_time_taken += total_week
            if COUNT is not 0:
                average_difficulty = total_sum_difficulty / COUNT
                average_num_attempts = total_sum_num_attempts / COUNT
                average_time_taken = total_sum_time_taken / COUNT
            return jsonify({'ReviewList' : serialize(reviews), 'average_difficulty' : average_difficulty, 'average_num_attempts' : average_num_attempts, 'average_time_taken' : (average_time_taken - average_time_taken % 4)/4}), 200

        elif category is None:
            return jsonify(serialize(CertReview.getAllReviews())), 200
    return jsonify("잘못된 요청"), 404

@app.route('/create_lect_review', methods=['POST'])
def create_lect_review():
    if request.is_json:
        school_name = request.get_json().get('school_name', None)
        lecture_name = request.get_json().get('lecture_name', None)
        lecture_id = request.get_json().get('lecture_id', None)
        username = request.get_json().get('username', None)
        content = request.get_json().get('content', None)
        semester = request.get_json().get('semester', None)
        rating = request.get_json().get('rating', None)
        load = request.get_json().get('load', None)
        grade = request.get_json().get('grade', None)

        if (school_name and lecture_name and lecture_id and username and
            content and load and grade and semester and rating):
            review = LectureReview.create(school_name, lecture_name, lecture_id, username, content, load, grade, semester, rating)
        else:
            return jsonify("정보 불충분"), 404
        if review:
            return jsonify(serialize(review)), 200
    return jsonify("잘못된 요청"), 500

@app.route('/get_lect_review', methods=['POST'])
def get_lect_review():
    if request.is_json:
        # "글쓴이", "강좌명". 아무것도 적지 않을시 모든 리뷰 리턴.
        category = request.get_json().get('category', None)
        keyword = request.get_json().get('keyword', None)
        if category is None or keyword is None:
            return jsonify(serialize(LectureReview.getAllReviews())), 200
        
        if category == '글쓴이':
            reviews = LectureReview.getReviewByUsername(keyword)
            return jsonify(serialize(reviews)), 200

        if category == '강좌ID':
            reviews = LectureReview.getReviewByLectID(keyword)
            return jsonify(serialize(reviews)), 200

    return jsonify("잘못된 요청"), 500

from user import *
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80')
