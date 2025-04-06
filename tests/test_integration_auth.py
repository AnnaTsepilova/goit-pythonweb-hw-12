from unittest.mock import Mock

import pytest
from sqlalchemy import select

from src.database.models import User
from tests.conftest import TestingSessionLocal

user_data = {
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
}

user_data_password_change = {
    "username": "SomePassUser",
    "email": "some_test_email@gmail.com",
    "password": "12345678",
}

change_password = {
    "new_password": "NewPassword",
    "confirm_password": "NewPassword",
    "reset_password_token": "Token",
}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data


def test_signup_exits(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Користувач з таким email вже існує"

def test_signup_name_exits(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post(
        "api/auth/register",
        json={
            "username": "agent007",
            "email": "someuser@gmail.com",
            "password": "12345678",
        },
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Користувач з таким іменем вже існує"


def test_email_confirmation(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/request_email", json=user_data)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Перевірте свою електронну пошту для підтвердження"

def test_email_password_reset(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response_create = client.post("api/auth/register", json=user_data_password_change)

    monkeypatch.setattr("src.api.auth.send_reset_password_email", mock_send_email)
    response = client.post("api/auth/reset-password", json=user_data_password_change)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Перевірте свою електронну пошту для підтвердження"

@pytest.mark.asyncio
async def test_password_not_match(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data_password_change.get("email"))
        )
        current_user = current_user.scalar_one_or_none()

    response = client.post(
        "api/auth/change-password",
        json={
            "new_password": "passs",
            "confirm_password": "NewPassword",
            "reset_password_token": current_user.password_reset_token,
        },
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Паролі не співпадають"

@pytest.mark.asyncio
async def test_password_short(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data_password_change.get("email"))
        )
        current_user = current_user.scalar_one_or_none()

    response = client.post(
        "api/auth/change-password",
        json={
            "new_password": "pas",
            "confirm_password": "pas",
            "reset_password_token": current_user.password_reset_token,
        },
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Пароль повинен бути не менше 8 символів"

@pytest.mark.asyncio
async def test_password_change(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data_password_change.get("email"))
        )
        current_user = current_user.scalar_one_or_none()

    change_password["reset_password_token"] = current_user.password_reset_token
    response = client.post("api/auth/change-password", json=change_password)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Пароль змінено"


def test_email_confirmation_not_exist(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post(
        "api/auth/request_email", json={"email": "someemail@gmail.com"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Електронна адреса не існує"


def test_email_incorrect_token(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    token = "abcde12345"
    response = client.get(f"api/auth/confirmed_email/{token}")
    assert response.status_code == 422, response.text
    data = response.json()
    assert data["detail"] == "Неправильний токен для перевірки електронної пошти"


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Користувач з таким email вже існує"

def test_not_confirmed_login(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Електронна адреса не підтверджена"

@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data

    response_token = client.post(
        "api/auth/refresh-token",
        json={
            "refresh_token": data["refresh_token"],
        },
    )
    assert response_token.status_code == 200, response_token.text
    data_token = response_token.json()

    assert "access_token" in data_token
    assert "refresh_token" in data_token
    assert "token_type" in data_token

def test_wrong_password_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": user_data.get("username"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"

def test_wrong_username_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": "username", "password": user_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"

def test_validation_error_login(client):
    response = client.post(
        "api/auth/login", data={"password": user_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data
