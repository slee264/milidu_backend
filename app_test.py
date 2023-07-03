import pytest
from application import app as flask_app
import json

@pytest.fixture()
def app():
    
    yield flask_app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

headers = {"Content-Type": "application/json"}

def test_certs_route(client):
    response = client.get('/certs')
    assert response.status_code == 200
    assert b"code" in response.data
    
def test_cert_stats_route(client):
    # get all certstats
    response = client.get('/cert_stats')
    assert response.status == '200 OK'
    assert b"name" in response.data
    assert b"pass_rate" in response.data
    
    # get one certstat
    response = client.get('/cert_stats?cert_code=7917')
    assert response.status == '200 OK'
    assert b"name" in response.data
    assert b"pass_rate" in response.data
    
    # no certstat
    response = client.get('/cert_stats?cert_code=9999')
    assert response.status == '404 NOT FOUND'
    assert b"name" not in response.data
    assert b"pass_rate" not in response.data
    assert b"message" in response.data
    
    # wrong certstat
    response = client.get('/cert_stats?cert_code=ab12')
    assert response.status == '404 NOT FOUND'
    assert b"name" not in response.data
    assert b"pass_rate" not in response.data
    assert b"message" in response.data

def test_cert_test_schedule_route(client):
    response = client.post('/cert_test_schedule')
    assert response.status == '404 NOT FOUND'
    assert b"not valid" in response.data
    
    # 공공 데이터 느림
    # response = client.post('schedule?cert_code=7917')
    # assert response.status == '200 OK'
    # assert b"종목명" in response.data

    # 공공 데이터 느림
    # response = client.post('/cert_test_schedule?cert_code=9999')
    # assert response.status == '404 NOT FOUND'
    # assert b"not found" in response.data
    
    response = client.post('/cert_test_schedule?cert_code=ab12')
    assert response.status == '404 NOT FOUND'
    assert b"not valid" in response.data
    
def test_get_unischedule_route(client):
    response = client.post('/get_unischedule')
    assert response.status == '200 OK'
    assert b'reg_start' in response.data
    
    response = client.post('/get_unischedule', data = json.dumps({"school_name": "서울대학교"}), headers=headers)
    assert response.status == '200 OK'
    assert b'reg_start' in response.data
    assert b'school_name' in response.data
    assert str.encode("서울대학교") in response.data
    
    response = client.post('/get_unischedule', data = json.dumps({"school_name": "서울대학"}), headers=headers)
    assert response.status == '200 OK'
    assert b'reg_start' in response.data
    assert b'school_name' in response.data
    assert str.encode("서울대학교") in response.data
    assert str.encode("남서울대학교") in response.data
    
def test_get_lecture_route(client):
    response = client.post('/get_lecture')
    assert response.status == '200 OK'
    assert b'lecture_type' in response.data
    
    response = client.post('/get_lecture', data=json.dumps({"school_name": "서울대학교"}), headers=headers)
    assert response.status == '200 OK'
    assert b'lecture_type' in response.data
    assert str.encode("서울대학교") in response.data
    
def test_create_cert_review_route(client):
    response = client.post('/create_cert_review')
    assert response.status == '404 NOT FOUND'
    
    # response = client.post('/create_cert_review', 
    #                        data=json.dumps({
    #                            "cert_name": "용접기능사",
    #                            "cert_id": 1,
    #                            "username": "leethfc11",
    #                            "time_taken": "3 months",
    #                            "difficulty": "상",
    #                            "recommend_book": "점프 투 파이썬",
    #                            "num_attempts": 2,
    #                            "content": "재밌었어요",
    #                        }), headers=headers)
    # print(response.text)
    # assert response.status == '200 OK'
    
def test_get_cert_review_route(client):
    response = client.post('/get_cert_review')
    assert response.status == '404 NOT FOUND'
    
    response = client.post('/get_cert_review', data = json.dumps({
        "category": "글쓴이",
        "keyword": "leethfc11"
    }), headers=headers)
    
    assert response.status == '200 OK'
    assert "leethfc11" in response.text
    
    response = client.post('/get_cert_review', data = json.dumps({
        "category": "자격증명",
        "keyword": "용접기능사"
    }), headers=headers)
    
    assert response.status == '200 OK'
    assert "용접기능사" in response.text
    
    response = client.post('/get_cert_review', data = json.dumps({
        "category": "자격증명",
        "keyword": "의사"
    }), headers=headers)
    
    assert response.status == '200 OK'
    assert "용접기능사" not in response.text
    
def test_create_lect_review_route(client):
    response = client.post('/create_lect_review')
    assert response.status == '500 INTERNAL SERVER ERROR'
    assert "잘못된 요청" in response.text
    
    response = client.post('/create_lect_review', headers=headers, data=json.dumps({}))
    assert response.status == "404 NOT FOUND"
    assert "정보 불충분" in response.text
    
    # response = client.post('/create_lect_review', headers=headers, data=json.dumps({
    #     "school_name": "서울대학교",
    #     "lecture_name": "Game Theory",
    #     "lecture_id": 24,
    #     "username": "leethfc11",
    #     "content": "재밌습니다",
    #     "num_likes": None,
    #     "load": "Not bad",
    #     "grade": "A-"
    # }))
    # assert response.status == '200 OK'
    # assert "leethfc11" in response.text
    
def test_get_lect_review_route(client):
    response = client.post('/get_lect_review')
    assert response.status == '500 INTERNAL SERVER ERROR'
    assert "잘못된 요청" in response.text
    
    response = client.post('/get_lect_review', headers=headers, data=json.dumps({}))
    assert response.status == '200 OK'
    
    response = client.post('/get_lect_review', headers=headers, data=json.dumps({
        "category": "글쓴이"
    }))
    assert response.status == '200 OK'
    assert "leethfc11" in response.text
    
    response = client.post('/get_lect_review', headers=headers, data=json.dumps({
        "category": "글쓴이",
        "keyword": "leethfc11"
    }))
    assert response.status == '200 OK'
    assert "leethfc11" in response.text
    
    response = client.post('/get_lect_review', headers=headers, data=json.dumps({
        "category": "강좌명",
        "keyword": "Game Theory"
    }))
    assert response.status == '200 OK'
    assert "Game Theory" in response.text
    
    
def test_signup_route(client):
    response = client.post('/signup')
    assert response.status == '500 INTERNAL SERVER ERROR'
    assert "잘못된 요청" in response.text
    
    response = client.post('/signup', headers=headers, data=json.dumps({}))
    assert response.status == '404 NOT FOUND'
    assert "잘못된 정보" in response.text
    
    response = client.post('/signup', headers=headers, data=json.dumps({
        "name": "이승훈"
    }))
    assert response.status == '404 NOT FOUND'
    assert "잘못된 정보" in response.text
    
    # response = client.post('/signup', headers=headers, data=json.dumps({
    #     "name": "이승훈",
    #     "username": "leethfc11",
    #     "password": "123"
    # }))
    # assert response.status == '200 OK'
    # assert "이승훈" in response.text
    
    response = client.post('/signup', headers=headers, data=json.dumps({
        "name": "이승훈",
        "username": "leethfc11",
        "password": "123"
    }))
    assert response.status == '404 NOT FOUND'
    assert "유저 등록 실패" in response.text
    
    
def test_login_route(client):
    response = client.post('/login')
    assert response.status == '500 INTERNAL SERVER ERROR'
    assert "잘못된 요청" in response.text
    
    response = client.post('/login', headers = headers, data=json.dumps({}))
    assert response.status == '404 NOT FOUND'
    assert "정보를 다시" in response.text
    
    response = client.post('/login', headers = headers, data=json.dumps({
        "username": "leethfc11"
    }))
    assert response.status == '404 NOT FOUND'
    assert "정보를 다시" in response.text
    
    response = client.post('/login', headers = headers, data=json.dumps({
        "username": "leethfc11",
        "password": "123"
    }))
    assert response.status == '200 OK'
    assert "leethfc11" in response.text
    
    response = client.post('/login', headers = headers, data=json.dumps({
        "username": "leethfc11",
        "password": "1234"
    }))
    assert response.status == '404 NOT FOUND'
    assert "로그인 실패" in response.text
    
# def logout_test(client):