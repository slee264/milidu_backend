import os
from flask import Flask, request
import requests
from models import bcrypt, db, Cert, CertStats, UniSchedule, UniLecture, User
import xml.etree.ElementTree as ET
import pandas as pd
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from ignore import secret_key, db_serviceKey
app = Flask("app")
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
# 임시!!!!!
app.secret_key = secret_key

db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

def get_new_lists():
    BODY = 1
    ITEMS = 0
    # 기술사 = 01, 기능장 = 02, 기사 = 03, 기능사 = 04
    SERIESCD = ['01', '02', '03', '04']
    # 기술사 = 10, 기능장 = 20, 기사 = 30, 기능사 = 40
    GRADECD = ['10', '20', '30', '40']
    YEARCD = ['2018', '2019', '2020', '2021', '2022']
    def get_certs(seriesCD: [str]):
        cert_dict = {}
        for cd in seriesCD:
            # cert_xml_url = 'http://openapi.q-net.or.kr/api/service/rest/InquiryQualInfo/getList'
            # cert_xml_params ={'serviceKey' : db_serviceKey, 'seriesCd' : cd }

            # cert_xml = requests.get(cert_xml_url, params=cert_xml_params)

            cert_xml_root = ET.parse("cert_xml_file_" + cd + ".xml").getroot()
            # f = open("cert_xml_file" + "_" + cd + ".txt", "wb")
            # f.write(cert_xml.content)
            # f.close()
            # print(cert_xml_root[1][0][0].find('implNm').text)

            for item in cert_xml_root[BODY][ITEMS]:
                val = []
                if item.find("engJmNm") is not None:
                    val.append(item.find("engJmNm").text)
                else:
                    val.append("")
                if item.find("jmCd") is not None:
                    val.append(item.find("jmCd").text)
                else:
                    val.append("FFFF")

                if item.find("instiNm") is not None:
                    val.append(item.find("instiNm").text)
                else:
                    val.append("")

                if item.find("implNm") is not None:
                    val.append(item.find("implNm").text)
                else:
                    val.append("")
                st = set()
                if item.find("mdobligFldNm") is not None:
                    lst = item.find("mdobligFldNm").text.split(".")
                    for s in lst:
                        st.add(s)

                cert_dict[item.find("jmNm").text] = val + [st]

        # related_major_url = 'http://openapi.q-net.or.kr/api/service/rest/InquiryMjrQualSVC/getList'
        # params ={'serviceKey' : db_serviceKey, 'grdCd' : '10', 'baseYY' : '2020', 'pageNo' : '1', 'numOfRows' : '95' }
        # related_major_xml = requests.get(related_major_url, params=params)
        # f = open("related_major.xml" , "wb")
        # f.write(related_major_xml.content)
        # f.close()
        # related_major_xml_root = ET.fromstring(related_major_xml.content)
        related_major_xml_root = ET.parse("related_major.xml").getroot()
        count = 0
        for item in related_major_xml_root[BODY][ITEMS]:
            if item.find("jmNm") is not None:
                name = item.find("jmNm").text
                redun = name.find("(")
                if redun >= 0:
                    name = name[:redun]
                if name in cert_dict:
                    if item.find("obligFldNm") is not None:
                        str_list = item.find("obligFldNm").text.split(".")
                        for s in str_list:
                            cert_dict[name][-1].add(s)
                    else:
                        count += 1
            else:
                count += 1

        for item in cert_dict.items():
            item = list(item)
            major_list_str = ""
            for major in item[1][4]:
                major_list_str += major + ", "
            row = Cert(item[0], item[1][0], item[1][1], item[1][2], item[1][3], major_list_str[:-2])
            db.session.add(row)
        db.session.commit()
        db.session.close()

    def get_certStats(gradeCD: [str], yearCD: [str]):
        stats_dict = {}
        for grcd in GRADECD:
            for yrcd in YEARCD:
                stats_xml_url = 'http://openapi.q-net.or.kr/api/service/rest/InquiryQualPassRateSVC/getList'
                stats_xml_params ={'serviceKey' : db_serviceKey, 'grdCd' : grcd, 'baseYY' : yrcd, 'pageNo' : '1', 'numOfRows' : '3000' }
                stats_xml = requests.get(stats_xml_url, params=stats_xml_params)
                stats_xml_root = ET.fromstring(stats_xml.content)
                for item in stats_xml_root[BODY][ITEMS]:
                    val = []
                    if item.find("examTypCcd").text == '실기':
                        if item.find("implYy").text is not None:
                            val.append(int(item.find("implYy").text))
                        else:
                            val.append("")

                        if item.find("recptNoCnt") is not None:
                            val.append(int(item.find("recptNoCnt").text))
                        else:
                            val.append("")

                        if item.find("examPassCnt") is not None:
                            val.append(int(item.find("examPassCnt").text))
                        else:
                            val.append("")

                        if item.find("jmFldNm").text not in stats_dict:
                            stats_dict[item.find("jmFldNm").text] = [val]
                        else:
                            # print(item.find("implYy").text)
                            # print(stats_dict[item.find("jmFldNm").text][-1][0])
                            if int(item.find("implYy").text) == stats_dict[item.find("jmFldNm").text][-1][0]:
                                for i in range(1, 3):
                                    stats_dict[item.find("jmFldNm").text][-1][i] += val[i]
                            else:
                                stats_dict[item.find("jmFldNm").text].append(val)

        for item in stats_dict.items():
            item = list(item)
            for data in item[1]:
                row = CertStats(item[0], data[0], data[1], data[2])
                db.session.add(row)
        db.session.commit()
        db.session.close()
    get_certs(SERIESCD)
    get_certStats(GRADECD, YEARCD)

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
    schedule_xml_params ={'serviceKey' : db_serviceKey, 'jmCd' : cert_code}
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


@app.route('/univ', methods=['GET'])
def university():
    df = pd.read_excel('excel/23.1 academic calendar.xlsx')
    NUM_ROWS = df.shape[0]
    COLS = df.columns
    for row in range(NUM_ROWS):
        cal_dict = {}
        for col in COLS:
            cal_dict[col] = df[col][row]
        db_row = UniSchedule(cal_dict['대학'], cal_dict['수강 신청일'], cal_dict['개강일'], cal_dict['수강신청 정정일'], cal_dict['수강 철회일'], cal_dict['종강일'])
        print(db_row)
        db.session.add(db_row)
    db.session.commit()
    db.session.close()

    return 'testing'

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

@app.route('/lecture', methods=['GET'])
def lecture():
    df = pd.read_excel('excel/23.1 univ lecture list.xlsx')
    NUM_ROWS = df.shape[0]
    NUM_COLS = df.shape[1]
    COLS = df.columns[1:]
    for row in range(NUM_ROWS):
        lecture_dict = {}
        for col in COLS:
            lecture_dict[col] = df[col][row]

        db_row = UniLecture(lecture_dict['수강대학'], lecture_dict['강좌명'], lecture_dict['대학과정코드'], lecture_dict['교수명'], lecture_dict['학점'],
                            lecture_dict['강좌이수구분'] if type(lecture_dict['강좌이수구분']) is str else "#N/A", lecture_dict['강좌정원'], 
                            lecture_dict['비용'], lecture_dict['수강료'], lecture_dict['신청시작일'])
        db.session.add(db_row)
    db.session.commit()
    db.session.close()
    return 'lectures!'

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80')
