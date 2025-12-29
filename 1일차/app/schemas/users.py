from enum import Enum
from pydantic import BaseModel


# 1. 성별 제한을 위한 Enum 클래스
class GenderEnum(str, Enum):
    male = "male"
    female = "female"


# 2. 유저 생성 요청 (POST /users)
class UserCreateRequest(BaseModel):
    username: str
    age: int
    gender: GenderEnum


# 3. 유저 수정 요청 (PATCH /users/{id})
class UserUpdateRequest(BaseModel):
    username: str | None = None
    age: int | None = None


# 4. 유저 응답 결과 (GET /users 등)
class UserResponse(BaseModel):
    id: int | None = None
    username: str | None = None
    age: int | None = None
    gender: GenderEnum | None = None

    # # UserModel 객체를 Pydantic 모델로 변환하기 위한 설정
    # class Config:
    #     from_attributes = True
