import asyncio
from src.models.orm_booking import Base
from src.core.db_conn import async_engine


async def create_tables() -> None:
    print(f"Путь к базе данных: {async_engine.url}")

    print(f" Зарегистрированные таблицы: {list(Base.metadata.tables.keys())}")

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_tables())
