from datetime import datetime
from pytz import timezone
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import Date, Column, Integer, String, Text, DateTime, ForeignKey

from database import Base, db_session


bcrypt = Bcrypt()

class Cert(Base):
    __tablename__ = "cert"
    def __init__(self, name, name_eng, code, ministry, host, related_majors, description):
        self.name = name
        self.name_eng = name_eng
        self.code = code
        self.ministry = ministry
        self.host = host
        self.related_majors = related_majors
        self.description = description
        
    def getAllCerts():
        return Cert.query.all()
    
    def getCertByCode(cert_code):
        return Cert.query.filter(Cert.code == cert_code).first()
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 자격증명
    name = Column(String(100), nullable=True)
    # 영문명
    name_eng = Column(String(100), nullable=True)
    # 자격증 코드
    code = Column(String(4), nullable=True)
    # 시험부처
    ministry = Column(String(100), nullable=True)
    # 주관기관
    host = Column(String(100), nullable=True)
    # 관련 전공
    related_majors = Column(String(100), nullable=True)
    # 자격증 설명 optional
    description = Column(Text, nullable=True)
    
    def __repr__(self):
        return f'<Certificate id = {self.id}, name = {self.name}, name_eng = {self.name_eng}, code = {self.code}, ministry = {self.ministry}, host = {self.host}, majors = {self.related_majors}>'
    
class CertStats(Base):
    __tablename__ = "cert_stats"
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
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 자격증 id
    cert_id = Column(Integer, ForeignKey('cert.id'), nullable=True)
    # 자격증 이름
    name = Column(String(50), nullable=False)
    # 응시 년도
    year = Column(Integer, nullable=False)
    # 총 응시자수
    total_taken = Column(Integer, nullable=True)
    # 총 합격자수
    total_passed = Column(Integer, nullable=True)
    # 군장병 응시자 수
    total_taken_m = Column(Integer, nullable=True)
    # 군장병 합격자 수
    total_passed_m = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f'<CertStats cert_id = {self.cert_id}, CertNAME = {self.name}, CertYEAR = {self.year}, total_taken = {self.total_taken}, total_passed = {self.total_passed}>'
    
class UniSchedule(Base):
    __tablename__ = "uni_schedule"
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
        
    def getAllSchedules():
        return UniSchedule.query.all()
    
    def getSchedule(school_name):
        schedule = UniSchedule.query.filter(UniSchedule.school_name == school_name).first()
        return schedule
    
    def getSimilarSchoolSchedules(school_name):
        return UniSchedule.query.filter(UniSchedule.school_name.contains(school_name)).all()
    id = Column(Integer, primary_key=True, autoincrement=True)
        
    # 학교명
    school_name = Column(String(20), nullable=False)
    
    # 수강신청시작
    reg_start = Column(Date, nullable=False)
    # 수강신청마감일
    reg_end = Column(Date, nullable=False)
    
    # 개강일
    sem_start = Column(Date, nullable=False)
    
    # 수강신청정정시작
    reg_change_start = Column(Date, nullable=False)
    # 수강신청정정마감
    reg_change_end = Column(Date, nullable=False)
    
    # 수강철회시작
    reg_cancel_start = Column(Date, nullable=False)
    # 수강철회마감
    reg_cancel_end = Column(Date, nullable=False)
    
    # 종강일
    sem_end = Column(Date, nullable=False)
    
    def __repr__(self):
        return f'< id = {self.id}, UniSchedule school_name = {self.school_name}, reg_start = {self.reg_start}, reg_end = {self.reg_end}, sem_start = {self.sem_start}, \
        reg_change_start = {self.reg_change_start}, reg_change_end = {self.reg_change_end}, reg_cancel_start = {self.reg_cancel_start}, reg_cancel_end = {self.reg_cancel_end}, \
        sem_end = {self.sem_end}>'
    
class UniLecture(Base):
    __tablename__ = "uni_lecture"
    def __init__(self, univ, lecture, code, prof, credit, lecture_type, max_seats, costs, tuition, reg_start):
        self.univ = univ
        self.lecture = lecture
        self.code = str(code)
        self.prof = prof
        self.credit = credit
        self.lecture_type = lecture_type
        self.max_seats = max_seats
        self.costs = costs
        self.tuition = tuition
        # reg_start = str(reg_start).strip()
        # self.reg_start = datetime(int(reg_start[:4]), int(reg_start[4:6]), int(reg_start[6:]))
        self.reg_start = reg_start
        
    def getAllLectures():
        return UniLecture.query.all()
    
    def getLectures(school_name):
        return UniLecture.query.filter(UniLecture.univ == school_name).all()
    id = Column(Integer, primary_key = True, autoincrement = True)

    #학교명
    univ = Column(String(20), nullable = False)

    #강좌명
    lecture = Column(String(50), nullable = False)

    #대학 과정 코드
    code = Column(String(20), nullable = False)

    #교수명
    prof = Column(String(20), nullable = False)
    
    #학점
    credit = Column(Integer, nullable = False)
    
    #강좌이수구분
    lecture_type = Column(String(10), nullable = False)
    
    #강좌 인원
    max_seats = Column(Integer, nullable = False)
    
    #비용
    costs = Column(Integer, nullable = False)
    
    #수강료
    tuition = Column(Integer, nullable = False)
    
    #수강신청 시작일
    reg_start = Column(String(20), nullable = False)
    
    
    def __repr__(self):
        return f'<UniLecture univ_name = {self.univ}, lecture = {self.lecture}, professor = {self.prof}, credit = {self.credit}, reg_start = {self.reg_start}>'

class User(UserMixin, Base):
    __tablename__ = "users"
    def __init__(self, name, username, pw):
        self.name = name
        self.username = username
        self.password = pw

    def signup(name, username, password):
        if not User.query.filter(User.name == name).first():
            pw_hash = bcrypt.generate_password_hash(password)
            user = User(name, username, pw_hash)
            db_session.add(user)
            db_session.commit()
            user = User.query.filter(User.id == user.id).first()
            return {"id": user.id, "name": user.name, "username": user.username}
            db_session.close()
        return None

    def authenticate(username, password):
        user = User.query.filter(User.username == username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            print("user authenticated")
            return {"id": user.id, "name": user.name, "username": user.username}
        return None

    def get(user_id):
        user = User.query.filter(User.id == user_id).first()
        return user

    id = Column(Integer, primary_key = True, autoincrement = True)

    #유저 이름
    name = Column(String(20), nullable = False)

    #유저 ID
    username = Column(String(20), nullable = False)

    #유저 비밀번호
    password = Column(Text, nullable = False)

    def __repr__(self):
        return f'<User name = {self.name}, username = {self.username}>'
    
class CertReview(Base):
    __tablename__ = "cert_review"
    def __init__(self, cert_name, cert_code, username, time_taken, difficulty, recommend_book, num_attempts, content, study_method, num_likes=0):
        
        self.cert_name = cert_name
        self.cert_code = cert_code
        self.username = username
        self.time_taken = time_taken
        self.difficulty = difficulty
        self.recommend_book = recommend_book
        self.num_attempts = num_attempts
        self.num_likes = num_likes
        self.content = content
        self.study_method = study_method
        #년 월 일 시 분 초 Micro초 타임존
        self.created_at = datetime.now(timezone('UTC')).astimezone(timezone('Asia/Seoul'))
        self.updated_at = self.created_at
        
    def create(cert_name, cert_code, username, time_taken, difficulty, recommend_book, num_attempts, content, study_method, num_likes):
        review = CertReview(cert_name, cert_code, username, time_taken, difficulty, recommend_book, num_attempts, content, study_method, num_likes)
        db_session.add(review)
        db_session.commit()
        
        return CertReview.query.filter(CertReview.id == review.id).first()
        db_session.close()
    
    def getReviewById(id):
        return CertReview.query.filter(CertReview.id == id).first()
    
    def getAllReviews():
        return CertReview.query.all()
    
    def getReviewByCertCode(cert_code):
        return CertReview.query.filter(CertReview.cert_code == cert_code).all()
    
    def getReviewByUsername(username):
        return CertReview.query.filter(CertReview.username == username).all()
        
    id = Column(Integer, primary_key = True, autoincrement = True)
    # 자격증 이름
    cert_name = Column(String(20), nullable = False)
    # 자격증 코드
    cert_code = Column(String(20), nullable = False)
    # 유저 ID
    username = Column(String(20), nullable = False)
    # 리뷰 내용
    content = Column(Text, nullable = True)
    #소요 시간
    time_taken = Column(String(20), nullable = False)
    #좋아요 수
    num_likes = Column(Integer, nullable = True)
    #난이도
    difficulty = Column(Integer, nullable = False)
    #추천 도서
    recommend_book = Column(String(50), nullable = True)
    #시도 횟수
    num_attempts = Column(Integer, nullable = False)
    #공부방법
    study_method = Column(String(50), nullable = True)
    #리뷰 쓰여진 시간+날짜
    created_at = Column(DateTime, nullable = False)
    #리뷰 업데이트 된 날짜
    updated_at = Column(DateTime, nullable = False)
    
    def __repr__(self):
        return f'<CertReview cert_name = {self.cert_name}, username = {self.username},\
 time_taken = {self.time_taken}, difficulty = {self.difficulty}, num_attempts = {self.num_attempts}, \
 num_likes = {self.num_likes}, content = {self.content}>'
    
class LectureReview(Base):
    __tablename__ = "lecture_review"
    def __init__(self, school_name, lecture_name, lecture_id, username, content, load, grade, num_likes=0):
        self.school_name = school_name
        self.lecture_name = lecture_name
        self.lecture_id = lecture_id
        self.username = username
        self.content = content
        self.num_likes = num_likes
        self.load = load
        self.grade = grade
        #년 월 일 시 분 초 Micro초 타임존
        self.created_at = datetime.now(timezone('UTC')).astimezone(timezone('Asia/Seoul'))
        self.updated_at = self.created_at

    def create(school_name, lecture_name, lecture_id, username, content, load, grade):
        review = LectureReview(school_name, lecture_name, lecture_id, username, content, load, grade)
        db_session.add(review)
        db_session.commit()
        return LectureReview.query.filter(LectureReview.id == review.id).first()
        db_session.close()
    
    def getAllReviews():
        return LectureReview.query.all()
    
    def getReviewByCertName(lecture_name):
        return LectureReview.query.filter(LectureReview.lecture_name == lecture_name).all()
    
    def getReviewByUsername(username):
        return LectureReview.query.filter(LectureReview.username == username).all()
    
    id = Column(Integer, primary_key = True, autoincrement = True)
    #대학교 이름
    school_name = Column(String(20), nullable = False)
    #강좌 이름
    lecture_name = Column(String(20), nullable = False)
    #강좌 ID
    lecture_id = Column(Integer, ForeignKey('uni_lecture.id'), nullable = False)
    #유저 ID
    username = Column(String(20), nullable = False)
    #리뷰 내용
    content = Column(Text, nullable = True)
    #좋아요 수
    num_likes = Column(Integer, nullable = True)
    #과제
    load = Column(String(20), nullable = False)
    #학점
    grade = Column(String(10), nullable = False)
    #리뷰 쓰여진 시간+날짜
    created_at = Column(DateTime, nullable = False)
    #리뷰 업데이트 된 날짜
    updated_at = Column(DateTime, nullable = False)
    
    def __repr__(self):
        return f'<LectureReview university = {self.school_name}, lecturename = {self.lecture_name}, username = {self.username}, content = {self.content}, load = {self.load}, grade = {self.grade}>'
    
class CertLecture(Base):
    __tablename__ = "cert_lecture"
    def __init__(self, cert_name, lecture_name, teacher, url):
        self.cert_name = cert_name
        self.lecture_name = lecture_name
        self.teacher = teacher
        self.url = url
        
    id = Column(Integer, primary_key = True, autoincrement = True)

    lecture_name = Column(String(50), nullable = False)
    
    cert_name = Column(String(50), nullable = False)
    
    teacher = Column(String(30), nullable = False)
    
    url = Column(String(100), nullable = False)
    
    def __repr__(self):
        return f'<CertLecture id = {self.id}, cert_name = {self.cert_name}, lecture_name = {self.lecture_name}, teacher = {self.teacher}, url = {self.url}>'
    