from datetime import date, datetime

from application.sql_helper import SQLHelper
from core.base_alg_object import BaseAlgObject
from core.db_instance import DBInstance


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
        result = SQLHelper.get_sms_templates()
        return result

    def create_user(self, user_data: dict) -> dict:
        password = user_data.pop('password')
        user_data['create_date'] = datetime.now()
        result = SQLHelper.create_user(user_data, password)
        return result
