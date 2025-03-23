from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas import ContactModel, ContactUpdate, ContactStatusUpdate

from src.database.models import User

class ContactService:
    def __init__(self, db: AsyncSession):
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactModel, user: User):
        return await self.contact_repository.create_contact(body, user)

    async def get_contacts(self, skip: int, limit: int, user: User):
        return await self.contact_repository.get_contacts(skip, limit, user)

    async def get_contact(self, contact_id: int, user: User):
        return await self.contact_repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User):
        return await self.contact_repository.update_contact(contact_id, body, user)

    async def update_status_contact(self, contact_id: int, body: ContactStatusUpdate, user: User):
        return await self.contact_repository.update_status_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        return await self.contact_repository.remove_contact(contact_id, user)

    async def search_contacts(self, search_field: str, query: str, skip: int, limit: int, user: User):
        return await self.contact_repository.search_contacts(search_field, query, skip, limit, user)

    async def birthdays_contacts(self, skip: int, limit: int, user: User):
        return await self.contact_repository.birthdays_contacts(skip, limit, user)
