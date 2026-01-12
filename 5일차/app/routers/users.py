from typing import Annotated, List

# Depends와 필요한 보안 관련 함수 임포트
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.models.users import UserModel
from app.schemas.users import UserCreateRequest, UserSearchParams, UserUpdateRequest
from app.utils.jwt import get_current_user

user_router = APIRouter(prefix="/users", tags=["user"])


@user_router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreateRequest):
    user = UserModel.create(**data.model_dump())
    return {"id": user.id}


# 2. 모든 유저 조회
@user_router.get("", response_model=List[UserModel])
async def get_all_users():
    result = UserModel.all()
    if not result:
        raise HTTPException(status_code=404, detail="Users not found")
    return result


# 3. 유저 검색 (Path 파라미터보다 위에 위치해야 함)
@user_router.get("/search")
async def search_users(query_params: Annotated[UserSearchParams, Query()]):
    valid_query = {k: v for k, v in query_params.model_dump().items() if v is not None}
    filtered_users = UserModel.filter(**valid_query)
    if not filtered_users:
        raise HTTPException(status_code=404, detail="No users match the criteria")
    return filtered_users


# 4. 내 정보 관련 (인증 필요)
@user_router.get("/me")
async def get_my_info(user: Annotated[UserModel, Depends(get_current_user)]):
    return user


@user_router.patch("/me")
async def update_my_info(
    user: Annotated[UserModel, Depends(get_current_user)],
    data: UserUpdateRequest,
):
    user.update(**data.model_dump(exclude_unset=True))
    return user


@user_router.delete("/me")
async def delete_my_account(user: Annotated[UserModel, Depends(get_current_user)]):
    user.delete()
    return {"detail": "Successfully Deleted."}


# 5. 특정 ID 유저 관련
@user_router.get("/{user_id}")
async def get_user_by_id(user_id: int = Path(gt=0)):
    user = UserModel.get(id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.patch("/{user_id}")
async def update_user_by_id(data: UserUpdateRequest, user_id: int = Path(gt=0)):
    user = UserModel.get(id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # exclude_unset=True를 사용하면 클라이언트가 보낸 값만 업데이트 가능.
    user.update(**data.model_dump(exclude_unset=True))
    return user


@user_router.delete("/{user_id}")
async def delete_user_by_id(user_id: int = Path(gt=0)):
    user = UserModel.get(id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.delete()
    return {"detail": f"User: {user_id}, Successfully Deleted."}
