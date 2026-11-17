from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from enterprise_rag.database.session import get_db_session
from enterprise_rag.schemas.user import UserCreate, UserResponse
from enterprise_rag.services.user import (
    UserAlreadyExistsError,
    UserService,
)

router = APIRouter(tags=["Users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    payload: UserCreate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserResponse:
    service = UserService(session)

    try:
        user = await service.create_user(
            email=str(payload.email),
            full_name=payload.full_name,
        )
        return UserResponse.model_validate(user)

    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/by-email/{email}",
    response_model=UserResponse,
)
async def get_user_by_email(
    email: str,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserResponse:
    service = UserService(session)
    user = await service.get_user_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return UserResponse.model_validate(user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserResponse:
    service = UserService(session)
    user = await service.get_user(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return UserResponse.model_validate(user)
