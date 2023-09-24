from flask import Flask, jsonify, request

from application.worker import Worker
from core.base_alg_object import BaseAlgObject
from core.token_helper import TokenHelper

app = Flask(__name__)
app.config['SECRET_KEY'] = 'css-secret-key'


class Main:
    logger = BaseAlgObject.logger
    logger.info(f'Starting CSS App')
    worker = Worker()
    session = {}

    @classmethod
    def start(cls):
        cls.worker.init()
        app.run(debug=True)


@app.route('/login', methods=['POST'], )
def login():
    username = request.json['username']
    password = request.json['password']
    if request.method == 'POST':
        result = Main.worker.login(username, password)
        print(f"result {result}")
        return jsonify(result)


@app.route('/sms_templates', methods=['GET'])
def sms_templates():
    if request.method == 'GET':
        authorization_header = request.headers.get('Authorization')
        token_res = TokenHelper.check_token(authorization_header[7:])
        if token_res['status'] is not 'ok':
            return jsonify(token_res)
        else:
            result = Main.worker.get_sms_templates()
            return jsonify(result)


@app.route('/user', methods=['POST'])
def user():
    user_data = request.json
    print(f"user data: {user_data}")
    if request.method == 'POST':
        result = Main.worker.create_user(user_data)
        return jsonify(result)


if __name__ == '__main__':
    Main.start()
