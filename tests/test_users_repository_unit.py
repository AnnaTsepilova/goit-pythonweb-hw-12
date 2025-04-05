import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repository.users import UserRepository
from src.schemas import User as UserModel
from src.schemas import UserCreate


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)


# @pytest.fixture
# def user():
#     return User(id=1, username="testuser")


@pytest.mark.asyncio
async def test_create_user(user_repository, mock_session):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        User(
            id=1,
            username="testuser",
            email="test02@test.com",
            avatar="http://some.url.com",
        )
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    user_create = UserCreate(
        username="testuser2", email="test02@test.com", password="secret_password"
    )
    # Call method
    user = await user_repository.create_user(
        body=user_create, avatar="http://some.url.com"
    )

    # Assertions
    assert user.username == "testuser2"
    assert user.email == "test02@test.com"
    assert user.avatar == "http://some.url.com"

@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, mock_session):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=1, username="testuser", email="test02@test.com", avatar="http://some.url.com"
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    user = await user_repository.get_user_by_id(user_id=1)

    # Assertions
    assert user.username == "testuser"
    assert user.email == "test02@test.com"
    assert user.avatar == "http://some.url.com"

@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, mock_session):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=1, username="NewUser", email="test02@test.com", avatar="http://some.url.com"
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    user = await user_repository.get_user_by_username(username="NewUser")

    # Assertions
    assert user.username == "NewUser"
    assert user.email == "test02@test.com"
    assert user.avatar == "http://some.url.com"

@pytest.mark.asyncio
async def test_confirm_email(user_repository, mock_session):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=1, username="testuser", email="test02@test.com", avatar="http://some.url.com"
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    await user_repository.confirmed_email(email="test02@test.com")
    user = await user_repository.get_user_by_email(email="test02@test.com")

    # Assertions
    assert user.username == "testuser"
    assert user.email == "test02@test.com"
    assert user.avatar == "http://some.url.com"
