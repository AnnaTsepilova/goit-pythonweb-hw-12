from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from enum import Enum

from src.database.db import get_db
from src.schemas import (
    ContactModel,
    ContactUpdate,
    ContactStatusUpdate,
    ContactResponse,
)
from src.services.contacts import ContactService
from src.services.auth import get_current_user
from src.database.models import User

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get contact by id

    Args:
        contact_id (int): Contact id
        db (AsyncSession, optional): db connection. Defaults to Depends(get_db).
        user (User, optional): Current logged user. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: HTTP_404_NOT_FOUND

    Returns:
        Contact by id
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


class SearchField(str, Enum):
    """Enum of avaliable search fields"""
    firstname = "firstname"
    lastname = "lastname"
    email = "email"

@router.get("/search/{field}", response_model=List[ContactResponse])
async def search_contacts(
    field: SearchField,
    skip: int = 0,
    limit: int = 100,
    query: str = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """_summary_

    Args:
        field (SearchField): Search field from SearchField enum
        skip (int, optional): Skip number of records. Defaults to 0.
        limit (int, optional): Limit number of results. Defaults to 100.
        query (str, optional): Search query. Defaults to None.
        db (AsyncSession, optional): db connection. Defaults to Depends(get_db).
        user (User, optional): Current logged user. Defaults to Depends(get_current_user).

    Returns:
        List of found contacts
    """
    contact_service = ContactService(db)
    contacts = await contact_service.search_contacts(
        search_field=field, query=query, skip=skip, limit=limit, user=user
    )
    return contacts


@router.get("/birthdays/", response_model=List[ContactResponse])
async def birthdays_contacts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get upcoming birthdays of contacts

    Args:
        skip (int, optional): Skip number of records. Defaults to 0.
        limit (int, optional): Limit number of results. Defaults to 100.
        db (AsyncSession, optional): db connection. Defaults to Depends(get_db).
        user (User, optional): Current logged user. Defaults to Depends(get_current_user).

    Returns:
        List of contacts with upcoming birthdays
    """
    contact_service = ContactService(db)
    contacts = await contact_service.birthdays_contacts(skip, limit, user)
    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create contact

    Args:
        body (ContactModel): Request body
        db (AsyncSession, optional): db connection. Defaults to Depends(get_db).
        user (User, optional): Current logged user. Defaults to Depends(get_current_user).

    Returns:
        Contact creation result
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactUpdate,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update contact

    Args:
        body (ContactUpdate): Request body
        contact_id (int): Contact id
        db (AsyncSession, optional): db connection. Defaults to Depends(get_db).
        user (User, optional): Current logged user. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: HTTP_404_NOT_FOUND

    Returns:
        Contact update result
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_status_contact(
    body: ContactStatusUpdate,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update contact status

    Args:
        body (ContactStatusUpdate): Request body
        contact_id (int): Contact id
        db (AsyncSession, optional): db connection. Defaults to Depends(get_db).
        user (User, optional): Current logged user. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: _description_

    Returns:
        Contact update result
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_status_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """_summary_

    Args:
        contact_id (int): Contact id
        db (AsyncSession, optional): db connection. Defaults to Depends(get_db).
        user (User, optional): Current logged user. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: HTTP_404_NOT_FOUND

    Returns:
        _type_: _description_
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
