"""
보안 및 인증 (Authentication Layer)
- 비밀번호 해싱 및 JWT 토큰 검증 처리
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from datetime import datetime
from models import User
from sqlalchemy import select

from database import get_db

# TODO: JWT 서명에 사용할 SECRET_KEY와 ALGORITHM(HS256)을 설정하세요
SECRET_KEY = "test"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINS = 30

# 비밀번호 암호화 컨텍스트 (argon2 알고리즘 사용)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# 토큰 추출을 위한 OAuth2 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 로그인한 유저 정보를 반환하는 함수
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    credential_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="무효한 토큰값"
    )

    """토큰 해독 후 현재 로그인한 유저 정보를 반환하는 의존성 함수"""
    try:
        # TODO: jwt.decode를 사용하여 토큰을 해독하고 유저네임(sub)을 추출하세요
        # TODO: DB에서 해당 유저를 조회(select)하여 변수 user에 저장하세요
        token_decode = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = token_decode.get("sub")
        exp = token_decode.get("exp")

        if username is None:
            raise HTTPException(status_code=401, detail="해당 유저가 존재하지 않습니다")

        if exp is None or (datetime.timestamp(exp) < datetime.now()):
            raise HTTPException(status_code=401, detail="토큰이 유효하지 않습니다")

        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        # 유저가 존재하지 않을 경우 401 에러 발생
        if not user:
            raise HTTPException(status_code=401, detail="인증 실패")

        return user
    except:
        # 토큰 무효화 등 예외 발생 시 401 에러 반환
        raise credential_error
