import base64
import uuid
from dataclasses import dataclass

TOKENS_DB = {}


@dataclass
class Provider:
    id: str
    name: str


@dataclass
class UserToken:
    access_token: str
    refresh_token: str
    provider: Provider


class TokenRepository:
    def __init__(self, db=TOKENS_DB):
        self._tokens = db

    def store(self, user_id, provider, token):
        p = Provider(id=provider['provider_id'], name=provider['display_name'])
        ut = UserToken(access_token=token.access,
                       refresh_token=token.refresh,
                       provider=p)

        user_tokens = self._tokens.get(user_id, [])
        if len(user_tokens) == 0:
            user_tokens = [ut]
        else:
            user_tokens.append(ut)

        self._tokens[user_id] = user_tokens

    def get_by_id(self, user_id):
        return self._tokens.get(user_id, [])


@dataclass
class User:
    id: str
    name: str


USERS_DB = [
    User(id=str(uuid.uuid4()), name='Alice'),
    User(id=str(uuid.uuid4()), name='Bob'),
    User(id=str(uuid.uuid4()), name='Charlie'),
]


class UserRepository:
    def __init__(self, db=USERS_DB):
        self._users = db

    def get_all(self):
        return self._users

    def get_by_id(self, id):
        for u in self._users:
            if u.id == id:
                return u
        return None


def encode_state(user_id):
    return base64.b64encode(user_id.encode('utf-8'))


def decode_state(state):
    return (base64.b64decode(state)).decode('utf-8')
