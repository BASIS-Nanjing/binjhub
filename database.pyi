from typing import *

class _Connection(Protocol):
    def cursor(self) -> _Cursor: ...
    def commit(self) -> Any: ...

class _Cursor(Protocol):
    def execute(self, sql: str, parameters: Sequence = ..., /) -> _Cursor: ...
    def fetchone(self) -> Sequence | None: ...
    def fetchall(self) -> Sequence[Sequence]: ...

RF_PENDING: int
RF_PLAYED: int
RF_DISAPPROVED: int
RF_ALL: int

UF_ADMIN: int
UF_SUSPENDED: int

class Database:
    def __init__(self, connect: Callable[[], _Connection]) -> None: ...
    def get_recommendations_by_user(
        self,
        email: str,
        skip: int = ...,
        top: int = ...,
        order_by: str = ...,
        flag: int | None = ...,
    ) -> list[Recommendation]: ...
    def get_votes_by_recommendation(
        self, recommendation_id: int, skip: int = ..., top: int = ...
    ) -> list[Vote]: ...
    def get_vote_counts_by_recommendation(
        self, recommendation_id: int
    ) -> tuple[int, int]: ...
    def get_votes_by_user(
        self, email: str, skip: int = ..., top: int = ...
    ) -> list[Vote]: ...
    def get_user_vote(self, email: str, recommendation_id: int) -> Vote | None: ...
    def get_recommendation_by_id(self, id: int) -> Recommendation: ...
    def get_vote_by_id(self, id: int) -> Vote: ...
    def get_user_by_email(self, email: str) -> User: ...
    def list_recommendations(
        self,
        skip: int = ...,
        top: int = ...,
        order_by: str = ...,
        flag: int | None = ...,
    ) -> list[Recommendation]: ...
    def add_user(self, email: str, name: str) -> bool: ...
    def add_recommendation(
        self, email: str, title: str, url: str, reason: str
    ) -> None: ...
    def update_vote(
        self, email: str, recommendation_id: int, up: bool, down: bool
    ) -> None: ...
    def patch_recommendation(
        self, id: int, *, reason: str | None = ..., flag: int | None = ...
    ) -> bool: ...
    def patch_user(self, id: int, *, flag: int) -> bool: ...
    def delete_recommendation(self, id: int) -> bool: ...
    def delete_vote(self, id: int) -> bool: ...

class Recommendation:
    id: int
    email: str
    title: str
    url: str
    reason: str
    flag: int
    created: int
    modified: int

class Vote:
    id: str
    recommendation_id: str
    email: str
    up: bool
    down: bool

class User:
    email: str
    name: str
    flag: int
