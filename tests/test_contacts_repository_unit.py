import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    return User(id=1, username="testuser")


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(
            id=1,
            firstname="firstname",
            lastname="lastname",
            email="test34@email.com",
            phone="380671234567",
            user=user,
        )
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contacts = await contact_repository.get_contacts(skip=0, limit=10, user=user)

    # Assertions
    assert len(contacts) == 1
    assert contacts[0].firstname == "firstname"
    assert contacts[0].lastname == "lastname"
    assert contacts[0].email == "test34@email.com"
    assert contacts[0].phone == "380671234567"


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1,
        firstname="firstname",
        lastname="lastname",
        email="test34@email.com",
        phone="380671234567",
        user=user,
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contact = await contact_repository.get_contact_by_id(contact_id=1, user=user)

    # Assertions
    assert contact is not None
    assert contact.id == 1
    assert contact.firstname == "firstname"
    assert contact.lastname == "lastname"
    assert contact.email == "test34@email.com"
    assert contact.phone == "380671234567"


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    # Setup
    contact_data = ContactModel(
        firstname="sdfsdfsdfwef",
        lastname="sdfsdfsdf",
        email="ffffffff@email.com",
        phone="380671222222",
        birthday="1980-01-01",
        description="Lorem ipsum description",
    )

    # Call method
    result = await contact_repository.create_contact(body=contact_data, user=user)

    # Assertions
    assert isinstance(result, Contact)
    assert result is not None
    assert result.firstname == "sdfsdfsdfwef"
    assert result.lastname == "sdfsdfsdf"
    assert result.email == "ffffffff@email.com"
    assert result.phone == "380671222222"
    assert result.birthday == date(1980, 1, 1)
    assert result.description == "Lorem ipsum description"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user):
    # Setup
    contact_data = ContactModel(
        firstname="updated",
        lastname="sdfsdfsdf",
        email="ffffffff@email.com",
        phone="380671222222",
        birthday="1980-01-01",
        description="Lorem ipsum description",
    )
    existing_contact = Contact(
        id=1,
        firstname="sdfsdfsdfwef",
        lastname="sdfsdfsdf",
        email="ffffffff@email.com",
        phone="380671222222",
        birthday="1980-01-01",
        description="Lorem ipsum description",
        user=user,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.update_contact(
        contact_id=1, body=contact_data, user=user
    )

    # Assertions
    assert result is not None
    assert result.firstname == "updated"
    assert result.lastname == "sdfsdfsdf"
    assert result.email == "ffffffff@email.com"
    assert result.phone == "380671222222"
    assert result.birthday == date(1980, 1, 1)
    assert result.description == "Lorem ipsum description"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_contact)


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user):
    # Setup
    existing_contact = Contact(
        id=1,
        firstname="firstname",
        lastname="lastname",
        email="test34@email.com",
        phone="380671234567",
        user=user,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.remove_contact(contact_id=1, user=user)

    # Assertions
    assert result is not None
    assert result.firstname == "firstname"
    assert result.lastname == "lastname"
    assert result.email == "test34@email.com"
    assert result.phone == "380671234567"
    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()
