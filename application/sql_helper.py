import base64

from werkzeug.datastructures import FileStorage

from core.db_instance import DBInstance


class SQLHelper:
    @classmethod
    def get_all(cls, table_name: str) -> list:
        sql_cmd = f"SELECT * FROM {table_name}"
        res = DBInstance.execute_sql(sql_cmd)
        return res

    @classmethod
    def get_by_id(cls, table_name: str, id_column_name: str, id_value: int) -> dict:
        sql_cmd = f"SELECT * FROM {table_name} WHERE {id_column_name}={id_value} AND is_active = True"
        res = DBInstance.execute_sql(sql_cmd)
        return res[0]

    @classmethod
    def get_user_by_username(cls, username: str) -> dict:
        sql_cmd = f"SELECT * FROM users WHERE username LIKE '{username}' AND is_active = True"
        res = DBInstance.execute_sql(sql_cmd)
        if len(res) == 0:
            return {'status': 'error', 'message': f"User with username '{username}' does not exist in DB"}
        else:
            return {'status': 'ok', 'result': res[0]}

    @classmethod
    def create_user(cls, fields_val_dict: dict, password: str) -> dict:
        insert_result = DBInstance.insert("users", fields_val_dict)
        if insert_result['status'] is not 'ok':
            return insert_result
        else:
            res = None
            new_user_id = insert_result['idusers']
            if new_user_id > 0:
                updated_user_id = DBInstance.update_user_password(new_user_id, password)
                if updated_user_id > 0:
                    res = cls.get_by_id('users', 'idusers', new_user_id)
            return {'status': 'ok', 'result': res}

    @classmethod
    def create_pdf_template(cls, file_name: str, file_bytes: bytes) -> dict:
        insert_result = DBInstance.insert_file(file_name, file_bytes)
        if insert_result['status'] is not 'ok':
            return insert_result
        else:
            new_file_id = insert_result['idpdf_templates']
            res = cls.get_by_id('pdf_templates', 'idpdf_templates', new_file_id)
            res['template_data'] = res['template_data'].decode()
            return {'status': 'ok', 'result': res}
