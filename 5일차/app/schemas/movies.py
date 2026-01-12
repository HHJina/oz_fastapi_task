# app/schemas/movies.py

from pydantic import BaseModel


# 1. 영화 생성 요청 (POST /movies)
class CreateMovieRequest(BaseModel):
    title: str
    playtime: int
    genre: list[str]


# 2. 영화 수정 요청 (PATCH /movies/{id})
class MovieUpdateRequest(BaseModel):
    title: str | None = None
    playtime: int | None = None
    genre: list[str] | None = None
