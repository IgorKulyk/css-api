import hashlib
import hmac
from datetime import datetime

from werkzeug.datastructures import FileStorage

from application.sql_helper import SQLHelper
from core.base_alg_object import BaseAlgObject
from core.db_instance import DBInstance
from core.token_helper import TokenHelper


def is_correct_password(salt: bytes, pw_hash: bytes, password: str) -> bool:
    """
    Given a previously-stored salt and hash, and a password provided by a user
    trying to log in, check whether the password is correct.
    """
    return hmac.compare_digest(
        pw_hash,
        hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    )


class Worker:
    def __init__(self):
        self.logger = BaseAlgObject.logger
        self.globals = {}

    def init(self):
        self.logger.debug('connecting to the DB')
        DBInstance.connect()
        self.logger.debug('worker is ready')

    # application api
    # ----------------------------------------
    def get_sms_templates(self) -> list:
        result = SQLHelper.get_all('sms_templates')
        return result

    def get_pdf_templates(self) -> list:
        result = SQLHelper.get_all('pdf_templates')
        return result

    def create_user(self, user_data: dict) -> dict:
        password = user_data.pop('password')
        user_data['create_date'] = datetime.now()
        result = SQLHelper.create_user(user_data, password)
        if result['status'] is not 'ok':
            return result
        else:
            response = result['result']
            response.pop('password_hash')
            response.pop('password_salt')
            return response

    def login(self, username: str, password: str) -> dict:
        response = SQLHelper.get_user_by_username(username)
        if response['status'] is not 'ok':
            return {'status': 'error', 'message': response['message']}
        else:
            user = response['result']
            db_salt = user['password_salt']
            db_hash = user['password_hash']
            if not is_correct_password(db_salt, db_hash, password):
                return {'status': 'error', 'message': 'Wrong password'}
            else:
                token = TokenHelper.create_token(user)
                logged_in_user = {
                    'username': user['username'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'phone': user['phone'],
                    'contact_email': user['contact_email']
                }
                return {'status': 'ok', 'user': logged_in_user, 'token': token}

    def create_pdf_template(self, file_name: str, file_bytes: bytes) -> dict:
        result = SQLHelper.create_pdf_template(file_name, file_bytes)
        return result
