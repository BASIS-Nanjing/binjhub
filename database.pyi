from typing import *

class _Connection(Protocol):
    def cursor(self) -> _Cursor: ...
    def commit(self) -> Any: ...

class _Cursor(Protocol):
    def execute(self, sql: str, parameters: Sequence = ..., /) -> _Cursor: ...
    def fetchone(self) -> Sequence | None: ...
    def fetchall(self) -> Sequence[Sequence]: ...

class Database:
    def __init__(self, connect: Callable[[], _Connection]) -> None: ...
    def get_recommendations_by_user(self, user_id: str) -> list[Recommendation]: ...
    def get_votes_by_recommendation(self, recommendation_id: str) -> list[Vote]: ...
    def get_votes_by_user(self, user_id: str) -> list[Vote]: ...
    def get_recommendation_by_id(self, id: str) -> Recommendation: ...
    def get_vote_by_id(self, id: str) -> Vote: ...
    def get_user_by_id(self, id: str) -> User: ...
    def list_recommendations(self, skip: int, top: int) -> list[Recommendation]: ...
    def add_recommendation(
        self, user_id: str, title: str, url: str, reason: str
    ) -> bool: ...
    def add_vote(self, user_id: str, recommendation_id: str) -> bool: ...
    def patch_recommendation(self, recommendation_id: str, **kwargs: str) -> None: ...
    def delete_recommendation(self, recommendation_id: str) -> bool: ...
    def delete_vote(self, vote_id: str) -> bool: ...

class Recommendation:
    id: str
    user_id: str
    title: str
    url: str
    reason: str

class Vote:
    id: str
    user_id: str
    recommendation_id: str

class User:
    id: str
    name: str
    email: str
