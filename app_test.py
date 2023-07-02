import pytest
from application import app as flask_app

@pytest.fixture()
def app():
    
    yield flask_app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

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
    
    response = client.post('/get_unischedule', data={"school_name": "서울대학교"})
    assert response.status == '200 OK'
    assert b'reg_start' in response.data
    assert b'school_name' in response.data
    
    response = client.post('/get_unischedule', data={"school_name": "서울대학"})
    assert response.status == '200 OK'
    assert b'reg_start' in response.data
    assert b'school_name' in response.data
    
def get_lecture_test(client):
    response = client.post('/get_lecture')
    
# def create_cert_review_test(client):
    
# def get_review_test(client):
    
# def create_lect_review_test(client):
    
# def get_lect_review_test(client):
    
# def login_test(client):
    
# def logout_test(client):
    
# def signup_test(client):