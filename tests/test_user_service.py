import asyncio
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from enterprise_rag.database.models import User
from enterprise_rag.services.user import (
    UserAlreadyExistsError,
    UserService,
)


def test_create_user_normalizes_email():
    async def run():
        session = AsyncMock()
        user = User(
            email="yash@example.com",
            full_name="Yash Gaikwad",
        )

        with patch("enterprise_rag.services.user.UserRepository") as repository_class:
            repository = repository_class.return_value
            repository.get_by_email = AsyncMock(return_value=None)
            repository.create = AsyncMock(return_value=user)

            service = UserService(session)

            result = await service.create_user(
                email="  YASH@EXAMPLE.COM  ",
                full_name="  Yash Gaikwad  ",
            )

            repository.get_by_email.assert_awaited_once_with("yash@example.com")
            repository.create.assert_awaited_once_with(
                email="yash@example.com",
                full_name="Yash Gaikwad",
            )
            session.commit.assert_awaited_once()
            session.refresh.assert_awaited_once_with(user)

            assert result.email == "yash@example.com"

    asyncio.run(run())


def test_create_user_rejects_duplicate_email():
    async def run():
        session = AsyncMock()
        existing_user = User(
            email="yash@example.com",
            full_name="Existing User",
        )

        with patch("enterprise_rag.services.user.UserRepository") as repository_class:
            repository = repository_class.return_value
            repository.get_by_email = AsyncMock(return_value=existing_user)
            repository.create = AsyncMock()

            service = UserService(session)

            with pytest.raises(UserAlreadyExistsError):
                await service.create_user(
                    email="YASH@example.com",
                    full_name="Another User",
                )

            repository.create.assert_not_awaited()
            session.commit.assert_not_awaited()

    asyncio.run(run())


def test_create_user_rolls_back_on_integrity_error():
    async def run():
        session = AsyncMock()

        with patch("enterprise_rag.services.user.UserRepository") as repository_class:
            repository = repository_class.return_value
            repository.get_by_email = AsyncMock(return_value=None)
            repository.create = AsyncMock(
                side_effect=IntegrityError(
                    "INSERT",
                    {},
                    Exception("duplicate"),
                )
            )

            service = UserService(session)

            with pytest.raises(UserAlreadyExistsError):
                await service.create_user(
                    email="yash@example.com",
                    full_name="Yash Gaikwad",
                )

            session.rollback.assert_awaited_once()
            session.commit.assert_not_awaited()

    asyncio.run(run())


def test_get_user_by_id():
    async def run():
        session = AsyncMock()
        user_id = uuid4()
        user = User(
            email="yash@example.com",
            full_name="Yash Gaikwad",
        )

        with patch("enterprise_rag.services.user.UserRepository") as repository_class:
            repository = repository_class.return_value
            repository.get_by_id = AsyncMock(return_value=user)

            service = UserService(session)
            result = await service.get_user(user_id)

            repository.get_by_id.assert_awaited_once_with(user_id)
            assert result is user

    asyncio.run(run())


def test_get_user_by_email_normalizes_email():
    async def run():
        session = AsyncMock()
        user = User(
            email="yash@example.com",
            full_name="Yash Gaikwad",
        )

        with patch("enterprise_rag.services.user.UserRepository") as repository_class:
            repository = repository_class.return_value
            repository.get_by_email = AsyncMock(return_value=user)

            service = UserService(session)

            result = await service.get_user_by_email(" YASH@EXAMPLE.COM ")

            repository.get_by_email.assert_awaited_once_with("yash@example.com")
            assert result is user

    asyncio.run(run())
