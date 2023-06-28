from datetime import datetime
from pytz import timezone
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class Cert(db.Model):
    def __init__(self, name, name_eng, code, ministry, host, related_majors):
        self.name = name
        self.name_eng = name_eng
        self.code = code
        self.ministry = ministry
        self.host = host
        self.related_majors = related_majors
        
    def getAllCerts():
        return Cert.query.all()
    
    def getCertByCode(cert_code):
        return Cert.query.filter(Cert.code == cert_code).first()
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 자격증명
    name = db.Column(db.String(100), nullable=True)
    # 영문명
    name_eng = db.Column(db.String(100), nullable=True)
    # 자격증 코드
    code = db.Column(db.String(4), nullable=True)
    # 시험부처
    ministry = db.Column(db.String(100), nullable=True)
    # 주관기관
    host = db.Column(db.String(100), nullable=True)
    # 관련 전공
    related_majors = db.Column(db.String(100), nullable=True)
    # 자격증 설명 optional
    description = db.Column(db.String(200), nullable=True)
    
    def __repr__(self):
        return f'<Certificate id = {self.id}, name = {self.name}, name_eng = {self.name_eng}, code = {self.code}, ministry = {self.ministry}, host = {self.host}, majors = {self.related_majors}>'
    
class CertStats(db.Model):
    def __init__(self, name, year, total_taken, total_passed):
        obj = Cert.query.filter(Cert.name == name).first()
        if obj is not None:
            self.cert_id = obj.id
        self.name = name
        self.year = year
        self.total_taken = total_taken
        self.total_passed = total_passed
        
    def getAllCertStats():
        return CertStats.query.all()
    
    def getCertStatsByCertId(cert_id):
        return CertStats.query.filter(CertStats.cert_id == cert_id).all()
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 자격증 id
    cert_id = db.Column(db.Integer, db.ForeignKey('cert.id'), nullable=True)
    # 자격증 이름
    name = db.Column(db.String(50), nullable=False)
    # 응시 년도
    year = db.Column(db.Integer, nullable=False)
    # 총 응시자수
    total_taken = db.Column(db.Integer, nullable=True)
    # 총 합격자수
    total_passed = db.Column(db.Integer, nullable=True)
    # 군장병 응시자 수
    total_taken_m = db.Column(db.Integer, nullable=True)
    # 군장병 합격자 수
    total_passed_m = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f'<CertStats cert_id = {self.cert_id}, CertNAME = {self.name}, CertYEAR = {self.year}, total_taken = {self.total_taken}, total_passed = {self.total_take}'
    
class UniSchedule(db.Model):
    def __init__(self, school_name, reg_dates, sem_start, reg_change_dates, reg_cancel_dates, sem_end_date):
        self.school_name = school_name
        
        reg_date_list = [date.strip().split('.') for date in reg_dates.split('~')]

        self.reg_start = datetime(int(reg_date_list[0][0]), int(reg_date_list[0][1]), int(reg_date_list[0][2]))
        self.reg_end = datetime(int(reg_date_list[1][0]), int(reg_date_list[1][1]), int(reg_date_list[1][2]))
        
        sem_start = sem_start.split('.')
        self.sem_start = datetime(int(sem_start[0]), int(sem_start[1]), int(sem_start[2]))
        
        reg_change_list = [date.strip().split('.') for date in reg_change_dates.split('~')]
        self.reg_change_start = datetime(int(reg_change_list[0][0]), int(reg_change_list[0][1]), int(reg_change_list[0][2]))
        self.reg_change_end = datetime(int(reg_change_list[1][0]), int(reg_change_list[1][1]), int(reg_change_list[1][2]))
        
        reg_cancel_list = [date.strip().split('.') for date in reg_cancel_dates.split('~')]
        self.reg_cancel_start = datetime(int(reg_cancel_list[0][0]), int(reg_cancel_list[0][1]), int(reg_cancel_list[0][2]))
        self.reg_cancel_end = datetime(int(reg_cancel_list[1][0]), int(reg_cancel_list[1][1]), int(reg_cancel_list[1][2]))
    
        sem_end = sem_end_date.split('.')
        self.sem_end = datetime(int(sem_end[0]), int(sem_end[1]), int(sem_end[2]))
        
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        
    # 학교명
    school_name = db.Column(db.String(20), nullable=False)
    
    # 수강신청시작
    reg_start = db.Column(db.Date, nullable=False)
    # 수강신청마감일
    reg_end = db.Column(db.Date, nullable=False)
    
    # 개강일
    sem_start = db.Column(db.Date, nullable=False)
    
    # 수강신청정정시작
    reg_change_start = db.Column(db.Date, nullable=False)
    # 수강신청정정마감
    reg_change_end = db.Column(db.Date, nullable=False)
    
    # 수강철회시작
    reg_cancel_start = db.Column(db.Date, nullable=False)
    # 수강철회마감
    reg_cancel_end = db.Column(db.Date, nullable=False)
    
    # 종강일
    sem_end = db.Column(db.Date, nullable=False)
    
    def __repr__(self):
        return f'< id = {self.id}, UniSchedule school_name = {self.school_name}, reg_start = {self.reg_start}, reg_end = {self.reg_end}, sem_start = {self.sem_start}, \
        reg_change_start = {self.reg_change_start}, reg_change_end = {self.reg_change_end}, reg_cancel_start = {self.reg_cancel_start}, reg_cancel_end = {self.reg_cancel_end}, \
        sem_end = {self.sem_end}>'
    
class UniLecture(db.Model):
    def __init__(self, univ, lecture, code, prof, credit, lecture_type, max_seats, costs, tuition, reg_start):
        self.univ = univ
        self.lecture = lecture
        self.code = code
        self.prof = prof
        self.credit = credit if type(credit) is int else credit.item()
        self.lecture_type = lecture_type
        self.max_seats = max_seats if type(max_seats) is int else max_seats.item()
        self.costs = costs if type(costs) is int else costs.item()
        self.tuition = tuition if type(tuition) is int else tuition.item()
        reg_start = str(reg_start).strip()
        self.reg_start = datetime(int(reg_start[:4]), int(reg_start[4:6]), int(reg_start[6:]))
        
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)

    #학교명
    univ = db.Column(db.String(20), nullable = False)

    #강좌명
    lecture = db.Column(db.String(50), nullable = False)

    #대학 과정 코드
    code = db.Column(db.Integer, nullable = False)

    #교수명
    prof = db.Column(db.String(20), nullable = False)
    
    #학점
    credit = db.Column(db.Integer, nullable = False)
    
    #강좌이수구분
    lecture_type = db.Column(db.String(10), nullable = False)
    
    #강좌 인원
    max_seats = db.Column(db.Integer, nullable = False)
    
    #비용
    costs = db.Column(db.Integer, nullable = False)
    
    #수강료
    tuition = db.Column(db.Integer, nullable = False)
    
    #수강신청 시작일
    reg_start = db.Column(db.Date, nullable = False)
    
    
    def __repr__(self):
        return f'<UniLecture univ_name = {self.univ}, lecture = {self.lecture}, professor = {self.prof}, credit = {self.credit}, reg_start = {self.reg_start}>'

class User(UserMixin, db.Model):

    def __init__(self, name, username, pw):
        self.name = name
        self.username = username
        self.password = pw

    def signup(name, username, password):
        if not User.query.filter(User.name == name).first():
            pw_hash = bcrypt.generate_password_hash(password)
            user = User(name, username, pw_hash)
            db.session.add(user)
            db.session.commit()
            db.session.close()
            return user
        return None

    def authenticate(username, password):
        user = User.query.filter(User.username == username).first()
        if bcrypt.check_password_hash(user.password, password):
            print("user authenticated")
            return user
        return None

    def get(user_id):
        user = User.query.filter(User.id == user_id).first()
        return user

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)

    #유저 이름
    name = db.Column(db.String(20), nullable = False)

    #유저 ID
    username = db.Column(db.String(20), nullable = False)

    #유저 비밀번호
    password = db.Column(db.String(20), nullable = False)

    def __repr__(self):
        return f'<User name = {self.name}, username = {self.username}>'
    
class CertReview(db.Model):
    def __init__(self, cert_name, cert_id, username, time_taken, difficulty, recommend_book, num_attempts, content, num_likes=0):
        
        self.cert_name = cert_name
        self.cert_id = cert_id
        self.username = username
        self.time_taken = time_taken
        self.difficulty = difficulty
        self.recommend_book = recommend_book
        self.num_attempts = num_attempts
        self.num_likes = num_likes
        self.content = content
        #년 월 일 시 분 초 Micro초 타임존
        self.created_at = datetime.now(timezone('UTC')).astimezone(timezone('Asia/Seoul'))
        
    def create(cert_name, cert_id, username, time_taken, difficulty, recommend_book, num_attempts, content, num_likes):
        review = CertReview(cert_name, cert_id, username, time_taken, difficulty, recommend_book, num_attempts, content, num_likes)
        db.session.add(review)
        db.session.commit()
        db.session.close()
        
        return CertReview.query.filter(CertReview.id == review.id).first()
    
    def getAllReviews():
        return CertReview.query.all()
    
    def getReviewByCertName(cert_name):
        return CertReview.query.filter(CertReview.cert_name == cert_name).all()
    
    def getReviewByUsername(username):
        return CertReview.query.filter(CertReview.username == username).all()
        
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    # 자격증 이름
    cert_name = db.Column(db.String(20), nullable = False)
    # 자격증 코드
    cert_id = db.Column(db.Integer, db.ForeignKey('cert.id'), nullable = False)
    # 유저 ID
    username = db.Column(db.String(20), nullable = False)
    # 리뷰 내용
    content = db.Column(db.Text, nullable = True)
    #소요 시간
    time_taken = db.Column(db.String(20), nullable = False)
    #좋아요 수
    num_likes = db.Column(db.Integer, nullable = True)
    #난이도
    difficulty = db.Column(db.Integer, nullable = False)
    #추천 도서
    recommend_book = db.Column(db.String(50), nullable = True)
    #시도 횟수
    num_attempts = db.Column(db.Integer, nullable = False)
    #리뷰 쓰여진 시간+날짜
    created_at = db.Column(db.DateTime, nullable = False)
    
    def __repr__(self):
        return f'<CertReview cert_name = {self.cert_name}, username = {self.username},\
 time_taken = {self.time_taken}, difficulty = {self.difficulty}, num_attempts = {self.num_attempts}, \
 num_likes = {self.num_likes}, content = {self.content}>'
    
class LectureReview(db.Model):
    def __init__(self, university, lecturename, lectureid, username, content, like_amount, load, grade):
        self.university = university
        self.lecturename = lecturename
        self.lectureid = lectureid
        self.username = username
        self.content = content
        self.like_amount = 0
        self.load = load
        self.grade = grade

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    
    #대학교 이름
    university = db.Column(db.String(20), nullable = False)
    
    #강좌 이름
    lecturename = db.Column(db.String(20), nullable = False)
    
    #강좌 ID
    lectureid = db.Column(db.Integer, db.ForeignKey('uni_lecture.id'), nullable = False)
    
    #유저 ID
    username = db.Column(db.String(20), nullable = False)
    
    #리뷰 내용
    content = db.Column(db.Text, nullable = True)
    
    #좋아요 수
    like_amount = db.Column(db.Integer, nullable = True)
    
    #과제
    load = db.Column(db.String(20), nullable = False)
    
    #학점
    grade = db.Column(db.String(10), nullable = False)
    
    def __repr__(self):
        return f'<LectureReview university = {self.university}, lecturename = {self.lecturename}, username = {self.username}, content = {self.content}, load = {self.load}, grade = {self.grade}>'