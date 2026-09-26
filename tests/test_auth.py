import json

def test_register_success(client):
    res = client.post('/api/v1/auth/register', json={
        'username': 'newwarrior',
        'password': 'password123',
        'email': 'warrior@example.com'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['user']['username'] == 'newwarrior'

def test_register_duplicate_username(client, test_user):
    res = client.post('/api/v1/auth/register', json={
        'username': test_user['username'],
        'password': 'password123'
    })
    assert res.status_code == 409
    data = res.get_json()
    assert data['success'] is False

def test_register_short_password(client):
    res = client.post('/api/v1/auth/register', json={
        'username': 'validuser',
        'password': '123'
    })
    assert res.status_code == 400
    data = res.get_json()
    assert 'at least 6 characters' in data['error']

def test_login_success(client, test_user):
    res = client.post('/api/v1/auth/login', json={
        'username': test_user['username'],
        'password': test_user['password']
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'access_token' in data

def test_login_invalid_password(client, test_user):
    res = client.post('/api/v1/auth/login', json={
        'username': test_user['username'],
        'password': 'WrongPassword!'
    })
    assert res.status_code == 401
    data = res.get_json()
    assert data['success'] is False

def test_refresh_token(client, test_user):
    res = client.post('/api/v1/auth/refresh', json={
        'refresh_token': test_user['refresh_token']
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'access_token' in data

def test_me_endpoint(client, auth_headers):
    res = client.get('/api/v1/auth/me', headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['user']['username'] == 'forgertest'
