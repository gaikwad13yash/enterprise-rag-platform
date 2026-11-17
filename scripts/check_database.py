import asyncio

from enterprise_rag.core.config import get_settings
from enterprise_rag.database.health import check_database_connection
from enterprise_rag.database.session import engine


async def main() -> None:
    settings = get_settings()

    try:
        is_connected = await check_database_connection(engine)

        if is_connected:
            print("PostgreSQL connection: SUCCESS")
            print(f"Database: {settings.postgres_db}")
            print(f"Host: {settings.postgres_host}:{settings.postgres_port}")
        else:
            print("PostgreSQL connection: FAILED")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
