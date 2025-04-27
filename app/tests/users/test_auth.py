from jose import jwt
from app.core.config import settings


def test_register_user(client):
    response = client.post(
        "/api/users/register",
        json={"email": "newuser@example.com", "name": "New User", "password": "newpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["name"] == "New User"
    assert "id" in data


def test_register_user_duplicate_email(client, test_user):
    response = client.post(
        "/api/users/register",
        json={"email": "test@example.com", "name": "Another User", "password": "anotherpass123"}
    )
    assert response.status_code == 400
    assert "Email уже зарегистрирован" in response.json()["detail"]


def test_login_user(client, test_user):
    response = client.post(
        "/api/users/login",
        json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    
    payload = jwt.decode(
        data["access_token"], 
        settings.SECRET_KEY, 
        algorithms=[settings.ALGORITHM]
    )
    assert str(test_user.id) == payload.get("sub")


def test_login_user_wrong_password(client, test_user):
    response = client.post(
        "/api/users/login",
        json={"email": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Неверные учетные данные" in response.json()["detail"]


def test_login_user_email_not_exists(client):
    response = client.post(
        "/api/users/login",
        json={"email": "nonexistent@example.com", "password": "somepassword"}
    )
    assert response.status_code == 401
    assert "Неверные учетные данные" in response.json()["detail"]


def test_refresh_token(client, test_user):
    login_response = client.post(
        "/api/users/login",
        json={"email": "test@example.com", "password": "password123"}
    )
    refresh_token = login_response.json()["refresh_token"]
    
    response = client.post(
        "/api/users/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    
    payload = jwt.decode(
        data["access_token"], 
        settings.SECRET_KEY, 
        algorithms=[settings.ALGORITHM]
    )
    assert str(test_user.id) == payload.get("sub")


def test_refresh_token_invalid(client):
    response = client.post(
        "/api/users/refresh",
        json={"refresh_token": "invalid_token"}
    )
    assert response.status_code == 401
    assert "Недействительный refresh токен" in response.json()["detail"]