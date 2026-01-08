"""
DB 모델 (Models Layer)
- SQLAlchemy 테이블 정의
"""

from database import Base
from sqlalchemy import Column, Integer, String, Float


class User(Base):
    """사용자 테이블"""

    __tablename__ = "users"

    # TODO: id, username(아이디), password(암호화된 비번), balance(잔액, float) 필드를 정의하세요
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(30), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)  # 이미 해시된 비밀번호 저장
    balance = Column(Float, nullable=False, default=0.0)

class Portfolio(Base):
    """포트폴리오 테이블"""

    __tablename__ = "portfolios"

    # TODO: id, username(소유자 아이디), symbol(종목코드), amount(보유수량), avg_price(매수평단가) 필드를 정의하세요
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(30), nullable=False)
    symbol = Column(String(30), nullable=False, index=True)
    amount = Column(Float, nullable=False, default=0.0)
    avg_price = Column(Float, nullable=False, default=0.0)
