import asyncio
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete

from enterprise_rag.database.models import User
from enterprise_rag.database.session import AsyncSessionFactory, engine
from enterprise_rag.main import app


def test_user_api_integration():
    email = f"api-test-{uuid4().hex[:12]}@example.com"
    full_name = "API Integration Test"

    try:
        with TestClient(app) as client:
            # 1. Create user
            response = client.post(
                "/api/v1/users",
                json={
                    "email": email,
                    "full_name": full_name,
                },
            )

            assert response.status_code == 201

            user_data = response.json()

            assert user_data["email"] == email
            assert user_data["full_name"] == full_name
            assert user_data["is_active"] is True

            user_id = user_data["id"]

            # 2. Duplicate email should return 409
            response = client.post(
                "/api/v1/users",
                json={
                    "email": email,
                    "full_name": full_name,
                },
            )

            assert response.status_code == 409

            # 3. Retrieve user by ID
            response = client.get(f"/api/v1/users/{user_id}")

            assert response.status_code == 200
            assert response.json()["email"] == email

            # 4. Retrieve user by email
            response = client.get(f"/api/v1/users/by-email/{email}")

            assert response.status_code == 200
            assert response.json()["id"] == user_id

            # 5. Invalid email should return 422
            response = client.post(
                "/api/v1/users",
                json={
                    "email": "invalid-email",
                    "full_name": full_name,
                },
            )

            assert response.status_code == 422

    finally:
        # Clean up using a single dedicated asyncio event loop.
        async def cleanup():
            async with AsyncSessionFactory() as session:
                await session.execute(delete(User).where(User.email == email))
                await session.commit()

            # Close pooled connections before this event loop exits.
            await engine.dispose()

        asyncio.run(cleanup())
