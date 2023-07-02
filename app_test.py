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
    
def test_stats_route(client):
    response = client.get('/stats')
    assert response.status == '200 OK'
    assert b"name" in response.data
    assert b"pass_rate" in response.data
    
    response = client.get('/stats?cert_code=7917')
    assert response.status == '200 OK'
    assert b"name" in response.data
    assert b"pass_rate" in response.data
    
    response = client.get('/stats?cert_code=9999')
    assert response.status == '404 NOT FOUND'
    assert b"name" not in response.data
    assert b"pass_rate" not in response.data
    
    response = client.get('/stats?cert_code=ab12')
    assert response.status == '404 NOT FOUND'
    assert b"name" not in response.data
    assert b"pass_rate" not in response.data

# def schedule_test(client):
    
# def get_uni_test(client):
    
# def get_lecture_test(client):
    
# def create_cert_review_test(client):
    
# def get_review_test(client):
    
# def create_lect_review_test(client):
    
# def get_lect_review_test(client):
    
# def login_test(client):
    
# def logout_test(client):
    
# def signup_test(client):
    
