import xml.etree.ElementTree as ET
import requests
import pandas as pd
import numpy as np
from psycopg2.extensions import register_adapter, AsIs
register_adapter(np.int64, AsIs)

from models import Cert, CertStats, UniSchedule, UniLecture, CertLecture
from config import DB_SERVICE_KEY
from database import db_session

def add_more_military_stats_engineer():
    df = pd.read_excel('excel/More_Detailed_Military_Stats.xlsx', sheet_name = '산업기사')
    NUM_ROWS = df.shape[0]
    NUM_COLS = df.shape[1]
    COLS = df.columns[:]
    YEARGROUP = [18, 19, 20, 21, 22]
    for row in range(NUM_ROWS):
        detailed_military_stats={}
        for col in COLS:
            detailed_military_stats[col] = df[col][row]
        if detailed_military_stats['종목'] != '합계':
            if type(detailed_military_stats['종목']) is str:
                cert_name = detailed_military_stats['종목']
            if detailed_military_stats['연도'] in YEARGROUP:
                detailed_military_stats['종목'] = cert_name
                detailed_military_stats['연도'] = '20' + str(detailed_military_stats['연도'])
                data = CertStats.query.filter(CertStats.name == detailed_military_stats['종목'] + '기사', CertStats.year == detailed_military_stats['연도']).first()
                if data:
                    data.total_taken_m = int(detailed_military_stats['응시'])
                    data.total_passed_m = int(detailed_military_stats['합격'])
                else:
                    data = CertStats.query.filter(CertStats.name == detailed_military_stats['종목'] + '산업기사', CertStats.year == detailed_military_stats['연도']).first()
                    if data:
                        data.total_taken_m = int(detailed_military_stats['응시'])
                        data.total_passed_m = int(detailed_military_stats['합격'])
    db_session.commit()
    db_session.close()

def add_more_military_stats_craftsman():
    df = pd.read_excel('excel/More_Detailed_Military_Stats.xlsx', sheet_name = '기능사')
    NUM_ROWS = df.shape[0]
    NUM_COLS = df.shape[1]
    COLS = df.columns[:]
    YEARGROUP = [18, 19, 20, 21, 22]
    for row in range(NUM_ROWS):
        detailed_military_stats={}
        for col in COLS:
            detailed_military_stats[col] = df[col][row]
        if type(detailed_military_stats['종목']) is str:
            cert_name = detailed_military_stats['종목']
        if detailed_military_stats['연도'] in YEARGROUP:
            detailed_military_stats['종목'] = cert_name
            detailed_military_stats['연도'] = '20' + str(detailed_military_stats['연도'])
            data = CertStats.query.filter(CertStats.name == detailed_military_stats['종목'] + '기능사', CertStats.year == detailed_military_stats['연도']).first()
            if data:
                data.total_taken_m = int(detailed_military_stats['응시'])
                data.total_passed_m = int(detailed_military_stats['합격'])
            else:
                data = CertStats.query.filter(CertStats.name == detailed_military_stats['종목'], CertStats.year == detailed_military_stats['연도']).first()
                if data:
                    data.total_taken_m = int(detailed_military_stats['응시'])
                    data.total_passed_m = int(detailed_military_stats['합격'])
    db_session.commit()
    db_session.close()

def cert_lecture():
    df = pd.read_excel('excel/Certs_Lecture.xlsx')
    NUM_ROWS = df.shape[0]
    NUM_COLS = df.shape[1]
    COLS = df.columns[:]
    for row in range(86, NUM_ROWS):
        cert_lecture_dict={}
        for col in COLS:
            cert_lecture_dict[col]=df[col][row]
        db_row = CertLecture(cert_lecture_dict['자격증 명'], cert_lecture_dict['강좌 명'], cert_lecture_dict['강사 명'], cert_lecture_dict['URL'])
        db_session.add(db_row)
    db_session.commit()
    db_session.close()

def add_military_stats():
    df = pd.read_excel('excel/Army_Certs_Stats.xlsx')
    NUM_ROWS = df.shape[0]
    NUM_COLS = df.shape[1]
    COLS = df.columns[1:]
    for row in range(86, NUM_ROWS):
        military_dict={}
        for col in COLS:
            military_dict[col]=df[col][row]
        if military_dict['자격증 종류'] != '계':
            if military_dict['자격증 종목'] == '산업기사':
                data = CertStats.query.filter(CertStats.name == military_dict['자격증 종류'] + '기사', CertStats.year == '2018').first()
                if data:
                    data.total_taken_m = int(military_dict['응시'])
                    data.total_passed_m = int(military_dict['합격'])
            elif military_dict['자격증 종목'] == '기능사':
                data = CertStats.query.filter(CertStats.name == military_dict['자격증 종류'] + '기능사', CertStats.year == '2018').first()
                if data:
                    data.total_taken_m = int(military_dict['응시'])
                    data.total_passed_m = int(military_dict['합격'])
            db_session.commit()
            db_session.close()

def add_service_stats():
    df = pd.read_excel('excel/test_certs_stats.xlsx', sheet_name = '2-1(서비스)')
    NUM_ROWS=df.shape[0]
    NUM_COLS=df.shape[1]
    COLS = df.columns[:]
    YEARGROUP = [18, 19, 20, 21, 22]
    for row in range(NUM_ROWS):
        service_stats_dict = {}
        for col in COLS:
            service_stats_dict[col] = df[col][row]
        if type(service_stats_dict['종목명']) is str:
            cert_name = service_stats_dict['종목명']
        if service_stats_dict['연도'] in YEARGROUP:
            service_stats_dict['종목명'] = cert_name
            service_stats_dict['연도'] = '20' + str(service_stats_dict['연도'])
            data = Cert.query.filter(Cert.name == service_stats_dict['종목명']).first()
            service_row = CertStats(service_stats_dict['종목명'], int(service_stats_dict['연도']), int(service_stats_dict['응시자']), int(service_stats_dict['합격자']))
            db_session.add(service_row)
    db_session.commit()
    db_session.close()

def uni_schedule():
    df = pd.read_excel('excel/23.1 academic calendar.xlsx')
    NUM_ROWS = df.shape[0]
    COLS = df.columns
    for row in range(NUM_ROWS):
        cal_dict = {}
        for col in COLS:
            cal_dict[col] = df[col][row]
        db_row = UniSchedule(cal_dict['대학'], cal_dict['수강 신청일'], cal_dict['개강일'], cal_dict['수강신청 정정일'], cal_dict['수강 철회일'], cal_dict['종강일'])
        db_session.add(db_row)
    db_session.commit()
    db_session.close()

    return 'testing'

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
        db_session.add(db_row)
    db_session.commit()
    db_session.close()
    return 'lectures!'


def get_new_lists():
    BODY = 1
    ITEMS = 0
    # 기술사 = 01, 기능장 = 02, 기사 = 03, 기능사 = 04
    SERIESCD = ['01', '02', '03', '04']
    # 기술사 = 10, 기능장 = 20, 기사 = 30, 기능사 = 40
    GRADECD = ['10', '20', '30', '31', '32', '33', '40']
    YEARCD = ['2018', '2019', '2020', '2021', '2022']
    def get_certs(seriesCD: [str]):
        cert_dict = {}
        for cd in seriesCD:
            # cert_xml_url = 'http://openapi.q-net.or.kr/api/service/rest/InquiryQualInfo/getList'
            # cert_xml_params ={'serviceKey' : DB_SERVICE_KEY, 'seriesCd' : cd }

            # cert_xml = requests.get(cert_xml_url, params=cert_xml_params)

            cert_xml_root = ET.parse("cert_xml_file_" + cd + ".xml").getroot()
            # f = open("cert_xml_file" + "_" + cd + ".txt", "wb")
            # f.write(cert_xml.content)
            # f.close()
            # print(cert_xml_root[1][0][0].find('implNm').ext)

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
                if item.find("summary") is not None:
                    val.append(item.find("summary").text)
                else:
                    val.append("")
                st = set()
                if item.find("mdobligFldNm") is not None:
                    lst = item.find("mdobligFldNm").text.split(".")
                    for s in lst:
                        st.add(s)
                cert_dict[item.find("jmNm").text] = val + [st]

        # related_major_url = 'http://openapi.q-net.or.kr/api/service/rest/InquiryMjrQualSVC/getList'
        # params ={'serviceKey' : DB_SERVICE_KEY, 'grdCd' : '10', 'baseYY' : '2020', 'pageNo' : '1', 'numOfRows' : '95' }
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
            for major in item[1][5]:
                major_list_str += major + ", "
            row = Cert(item[0], item[1][0], item[1][1], item[1][2], item[1][3], major_list_str[:-2], item[1][4])
            db_session.add(row)
        db_session.commit()
        db_session.close()

    def get_certStats(gradeCD: [str], yearCD: [str]):
        stats_dict = {}
        for grcd in gradeCD:
            for yrcd in yearCD:
                stats_xml_url = 'http://openapi.q-net.or.kr/api/service/rest/InquiryQualPassRateSVC/getList'
                stats_xml_params ={'serviceKey' : DB_SERVICE_KEY, 'grdCd' : grcd, 'baseYY' : yrcd, 'pageNo' : '1', 'numOfRows' : '1800' }
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
                db_session.add(row)
        db_session.commit()
        db_session.close()

    def add_service_certs():
            df = pd.read_excel('excel/service_Certs.xlsx')
            NUM_ROWS = df.shape[0]
            NUM_COLS = df.shape[1]
            COLS = df.columns
            for row in range(NUM_ROWS):
                service_dict={}
                for col in COLS:
                    service_dict[col] = df[col][row]
                row = Cert(service_dict['name'], service_dict['name_eng'] if type(service_dict['name_eng']) is str else "", str(service_dict['code']), service_dict['ministry'], service_dict['host'], service_dict['majors'], '')
                db_session.add(row)
            db_session.commit()
            db_session.close()

    get_certs(SERIESCD)
    add_service_certs()
    get_certStats(GRADECD, YEARCD)
    add_military_stats()
    add_service_stats()
    uni_schedule()
    lecture()