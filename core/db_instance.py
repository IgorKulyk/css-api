import hashlib
import os
from datetime import datetime
from typing import Tuple

import mysql
import mysql.connector
from mysql.connector import MySQLConnection

from core.base_alg_object import BaseAlgObject


def hash_new_password(password: str) -> Tuple[bytes, bytes]:
    """
    Hash the provided password with a randomly-generated salt and return the
    salt and hash to store in the database.
    """
    salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt, pw_hash


class SQLDBException(Exception):
    pass


def db_call(function):
    def wrapper(cls, *args, **kwargs):
        try:
            if DBInstance.is_connected():
                res = function(cls, *args, **kwargs)
            else:
                raise SQLDBException("DBInstance is not connected")
        except Exception as ex:
            BaseAlgObject.logger.exception(ex)
            raise SQLDBException(ex)
        return res
    return wrapper


class DBInstance:
    db_config = BaseAlgObject.config['DB']
    connect_info = {
        'host': db_config['server'], 'database': db_config['db_name'],
        'user': db_config['user'], 'password': db_config['password'],
        'raise_on_warnings': True,
        'auth_plugin': 'mysql_native_password'
    }
    connection: MySQLConnection = None
    cursor = None

    @classmethod
    def connect(cls):
        try:
            cls.connection = mysql.connector.connect(**cls.connect_info)
            cls.cursor = cls.connection.cursor()
        except Exception as ex:
            cls.generate_exception("connect", ex)

    @classmethod
    def disconnect(cls):
        try:
            cls.cursor.close()
            cls.connection.close()
        except Exception as ex:
            cls.generate_exception("disconnect", ex)

    @classmethod
    def is_connected(cls):
        return cls.connection is not None and cls.cursor is not None

    @staticmethod
    def generate_exception(info: str, exception: Exception):
        line = f"@@@ SQL DB Exception in {info}"
        BaseAlgObject.logger.error(line)
        BaseAlgObject.logger.error(f'exception: {exception}')
        raise SQLDBException(line)

    @classmethod
    @db_call
    def execute_sql(cls, sql_cmd: str) -> list:
        try:
            res = cls.cursor.execute(sql_cmd)
            res = cls.cursor.fetchall()
            results = []
            for index, value in enumerate(res):
                record_data = {
                    DBInstance.cursor.description[i][0]: value[i] for i in range(len(value))
                }
                results.append(record_data)
        except Exception as ex:
            results = None
            cls.generate_exception(f"execute_sql: {sql_cmd}", ex)
        return results

    @classmethod
    @db_call
    def insert(cls, table_name: str, fields_val_dict: dict) -> dict:
        field_names = ""
        for field_name in fields_val_dict.keys():
            field_names += f"{field_name}, "
        field_names = field_names[:-2]
        field_values = ""
        for value in fields_val_dict.values():
            if type(value) == str:
                field_values += f"'{value}', "
            elif type(value) == datetime:
                field_values += f"'{value}', "
            else:
                field_values += f"{value}, "
        field_values = field_values[:-2]
        sql_cmd = f"INSERT INTO {table_name} ({field_names}) VALUES ({field_values})"
        try:
            cls.cursor.execute(sql_cmd)
            cls.connection.commit()
            item_id = cls.cursor.lastrowid
            return {'status': 'ok', 'idusers': item_id}
        except Exception as ex:
            return {'status': 'error', 'message': str(ex)}

    @classmethod
    @db_call
    def update_user_password(cls, user_id: int, password: str) -> int:
        password_salt, password_hash = hash_new_password(password)
        sql_cmd = '''UPDATE users SET password_hash = _binary %s, password_salt = _binary %s WHERE idusers = %s'''
        cls.cursor.execute(sql_cmd, (password_hash, password_salt, user_id))
        cls.connection.commit()
        return user_id

    @classmethod
    @db_call
    def delete(cls, table_name: str, where_clause: str):
        sql_cmd = f"DELETE FROM {table_name} WHERE {where_clause}"
        res = cls.execute_sql(sql_cmd)
        cls.db.commit()
        return res

    @classmethod
    @db_call
    def update(cls, table_name: str, fields_val_dict: dict, where_clause: str):
        fields = ""
        for field_name, value in fields_val_dict.items():
            if type(value) == str:
                fields += f"{field_name} = '{value}', "
            else:
                fields += f"{field_name} = {value}, "
        fields = fields[:-2]
        sql_cmd = f"UPDATE {table_name} SET {fields} WHERE {where_clause}"
        res = cls.execute_sql(sql_cmd)
        cls.db.commit()
        return res

    @classmethod
    @db_call
    def select(cls, table_name: str, where_clause: str = None, order_by: str = None):
        sql_cmd = f"SELECT * FROM {table_name}"
        if where_clause is not None:
            sql_cmd += f" WHERE {where_clause}"
        if order_by is not None:
            sql_cmd += f" ORDER BY {order_by}"
        print(f"SQL QUERY: {sql_cmd}")
        res = cls.execute_sql(sql_cmd)
        return res
