from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from enterprise_rag.database.models import User
from enterprise_rag.repositories import UserRepository


class UserAlreadyExistsError(Exception):
    pass


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session)

    async def create_user(
        self,
        email: str,
        full_name: str,
    ) -> User:
        normalized_email = email.strip().lower()

        existing_user = await self.repository.get_by_email(normalized_email)

        if existing_user:
            raise UserAlreadyExistsError("A user with this email already exists.")

        try:
            user = await self.repository.create(
                email=normalized_email,
                full_name=full_name.strip(),
            )

            await self.session.commit()
            await self.session.refresh(user)

            return user

        except IntegrityError as exc:
            await self.session.rollback()
            raise UserAlreadyExistsError("A user with this email already exists.") from exc

    async def get_user(self, user_id: UUID) -> User | None:
        return await self.repository.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        normalized_email = email.strip().lower()
        return await self.repository.get_by_email(normalized_email)
