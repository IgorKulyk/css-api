from core.db_instance import DBInstance


class SQLHelper:
    @classmethod
    def get_sms_templates(cls) -> list:
        sql_cmd = f"SELECT * FROM sms_templates"
        res = DBInstance.execute_sql(sql_cmd)
        return res

    @classmethod
    def get_user_by_id(cls, user_id: int) -> dict:
        sql_cmd = f"SELECT * FROM users WHERE idusers={user_id} AND is_active = True"
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
                    res = cls.get_user_by_id(new_user_id)
            return {'status': 'ok', 'result': res}
