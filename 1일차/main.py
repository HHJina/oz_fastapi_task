from fastapi import FastAPI, HTTPException, Query

from app.models.users import UserModel

from app.schemas.users import UserCreateRequest, UserResponse, UserUpdateRequest

from typing import Annotated

app = FastAPI()

# 서버 시작 시 더미 데이터 생성
UserModel.create_dummy()


@app.get("/")
async def root() -> dict[str, str]:
    return {"Hello": "World"}


# 유저생성
@app.post("/users")
def create_user(request: UserCreateRequest):
    user = UserModel.create(username=request.username, age=request.age, gender=request.gender.value)
    return user


# 모든유저
@app.get("/users")
def get_all_users():
    return UserModel.all()

# 유저조회(복수)
@app.get("/users/search")
async def search_users(query_params: Annotated[UserResponse, Query()]):
    valid_query = {key: value for key, value in query_params.model_dump().items() if value is not None}
    filtered_users = UserModel.filter(**valid_query)
    if not filtered_users:
        raise HTTPException(status_code=404)

    return filtered_users


# 유저조회(단건)
@app.get("/users/{user_id}")
def get_user_by_id(user_id: int):
    user = UserModel.get(id=user_id)
    if user is None:
        raise HTTPException(status_code=404)

    return user

# 유저수정
@app.patch("/users/{user_id}")
def update_user(user_id: int, request: UserUpdateRequest):
    user = UserModel.get(id=user_id)
    if user is None:
        raise HTTPException(status_code=404)
    user.update(**request.model_dump())

    return user

# 유저삭제
@app.delete("/users/{user_id}")
def delete_user(user_id: int) -> dict[str, int]:
    user = UserModel.get(id=user_id)
    if user is None:
        raise HTTPException(status_code=404)
    user.delete()

    return {"delete_id": user_id}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
