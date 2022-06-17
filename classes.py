from enum import Enum

from pydantic import BaseModel


class Sex(Enum):
    UNKNOWN = 'unknown'
    MALE = 'male'
    FEMALE = 'female'


class Role(Enum):
    OWNER = 'owner'
    ADMIN = 'admin'
    MEMBER = 'member'


class User(BaseModel):
    group_id: int
    user_id: int
    nickname: str
    card: str
    sex: Sex
    # sex: str
    age: int
    area: str
    join_time: int
    last_sent_time: int
    level: str
    role: Role
    # role: str
    unfriendly: bool
    title: str
    title_expire_time: int
    card_changeable: bool
    shut_up_timestamp: int
