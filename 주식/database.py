"""
DB 설정 (Database Layer)
- 비동기 엔진 및 세션 생성
"""

from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./trading_game.db"

# TODO: create_async_engine을 사용하여 비동기 엔진을 생성하세요
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # SQL 쿼리 로그 출력
)

# TODO: async_sessionmaker를 사용하여 세션 로컬 클래스를 생성하세요
async_session = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# ORM 모델용 베이스 클래스
Base = declarative_base()


async def get_db():
    """비동기 DB 세션 생성 및 반환"""
    # TODO: async_session을 사용하여 세션을 열고 yield로 반환하세요
    async with async_session() as session:
        yield session
