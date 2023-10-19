from datetime import datetime, timedelta, timezone

import jwt

from core.base_alg_object import BaseAlgObject


class TokenHelper:
    token_secret = BaseAlgObject.config['Security']['token_secret']

    @classmethod
    def create_token(cls, user: dict) -> str:
        now = datetime.now(tz=timezone.utc)
        expires = now + timedelta(days=7)
        token = jwt.encode({
            "idusers": user['idusers'],
            "iat": now,
            "exp": expires,
        }, cls.token_secret, algorithm="HS256")
        return token

    @classmethod
    def check_token(cls, token: str) -> dict:
        try:
            decoded = jwt.decode(token, cls.token_secret, algorithms="HS256")
            print(f'decoded token: {decoded}')
            return {'status': 'ok', 'token': decoded}
        except Exception as ex:
            print(f"ex: {ex}")
            return {'status': 'error', 'message': str(ex)}
